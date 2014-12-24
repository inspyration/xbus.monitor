from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPFound
from pyramid.security import authenticated_userid
from pyramid.security import forget
from pyramid.security import NO_PERMISSION_REQUIRED
from pyramid.security import remember
from pyramid.view import forbidden_view_config

from xbus.monitor.auth import get_user_principals
from xbus.monitor.utils.singleton import Singleton

try:
    import lasso
    lasso_loaded = True
except:
    lasso_loaded = False


class LassoSingle(object):
    __metaclass__ = Singleton

    def __init__(self, sp_meta, sp_key, idp_meta):
        """
        @param sp_meta: filename of the metadata file for the service provider
        @type sp_meta: string

        @param sp_key: filename of the service provider key
        @type sp_key: string

        @param idp_meta: filename of the Identity provider metadata.xml file
        @type idp_meta: string
        """
        self.reads, errors = self.__read_conf_file(sp_meta, sp_key, idp_meta)

        if errors:
            raise HTTPForbidden(detail=u"\n".join(errors))

        self.sp_meta_xml = self.reads[0]
        self.sp_key = self.reads[1]
        self.idp_meta_xml = self.reads[2]

        self.server = lasso.Server.newFromBuffers(
            self.sp_meta_xml,
            self.sp_key
        )

        self.server.addProviderFromBuffer(
            lasso.PROVIDER_ROLE_IDP,
            self.idp_meta_xml
        )

    def __read_conf_file(self, *args):
        res = []
        errs = []
        for arg in args:
            try:
                with open(arg, 'r') as f:
                    res.append(f.read())
            except IOError as e:
                errs.append(str(e))
        return res, errs

    def get_login(self):
        """create a new login instance for each request.
        """
        return lasso.Login(self.server)


def _login_referrer(request, params):
    """Extract a "login_referrer" parameter from the specified dictionary or
    just provide an URL to the home page.
    """
    return params.get('login_referrer') or request.route_url('home')


def forbidden_view(exc, request):
    request.response.status = exc.code
    return {
        'auth_kind': request.registry.settings.auth_kind,
        'logged_in': request.authenticated_userid is not None,
    }


def login_view(request):
    """Redirect to either the login page or the previous page.
    Request params:
        * login_referrer (optional): The page to redirect to when logged in.
    """

    ret = {'auth_kind': request.registry.settings.auth_kind}

    login_referrer = _login_referrer(request, request.params)

    if authenticated_userid(request):
        ret['login_url'] = login_referrer
        return ret

    # Save the previous page.
    request.session['login_referrer'] = login_referrer

    # Redirect to Authentic.

    sp_meta = request.registry.settings['saml2.sp_meta']
    sp_key = request.registry.settings['saml2.priv_key']
    idp_meta = request.registry.settings['saml2.idp_meta']

    login = LassoSingle(sp_meta, sp_key, idp_meta).get_login()

    login.initAuthnRequest()
    login.request.nameIdPolicy.format = None
    login.request.nameIdPolicy.allowCreate = True
    login.buildAuthnRequestMsg()

    ret['login_url'] = login.msgUrl
    return ret


def login_metadata_view(request):
    with open(
        request.registry.settings['saml2.sp_meta'], 'r'
    ) as sp_meta_file:
        sp_meta = sp_meta_file.read()
    request.response.content_type = 'text/xml'
    return sp_meta


def login_success_view(request):
    """Called when the user has been redirected back to our site from the SAML2
    provider.
    Conclude the handshake, fetch some information (such as the user name,
    security groups...) and redirect to the home page.
    """

    sp_meta = request.registry.settings['saml2.sp_meta']
    sp_key = request.registry.settings['saml2.priv_key']
    idp_meta = request.registry.settings['saml2.idp_meta']

    login = LassoSingle(sp_meta, sp_key, idp_meta).get_login()

    saml_response = request.params.get('SAMLResponse', None)
    if not saml_response:
        raise HTTPForbidden('%s: %s' % (
            _('Login error'), _('No "SAMLResponse" parameter')
        ))
    try:
        login.processAuthnResponseMsg(saml_response)
    except (lasso.DsError, lasso.ProfileCannotVerifySignatureError):
        raise HTTPForbidden('%s: %s' % (
            _('Login error'), _('Invalid signature')
        ))
    except lasso.Error as e:
        raise HTTPForbidden('%s: %s' % (_('Login error'), str(e)))
    try:
        login.acceptSso()
    except lasso.Error as e:
        raise HTTPForbidden('%s: %s' % (_('Login error'), str(e)))

    # Read authentic attributes to fetch the user role.
    attributes = {}
    for att_statement in login.assertion.attributeStatement:
        for at in att_statement.attribute:
            values = attributes.setdefault(at.name, [])
            for value in at.attributeValue:
                content = [v.exportToXml() for v in value.any]
                content = ''.join(content)
                values.append(content)
    roles = attributes.get('role')
    if not roles:
        raise HTTPForbidden('%s: %s' % (
            _('Login error'), _('The authentic login is not in a group')
        ))

    request.session['authentic_roles'] = roles

    login_referrer = _login_referrer(request, request.session)
    headers = remember(request, login.assertion.subject.nameId.content)

    return HTTPFound(location=login_referrer, headers=headers)


def logout_view(request):
    """Just empty the session and let the client handle this."""
    request.session.clear()
    request.response.headerlist.extend(forget(request))
    return {'auth_kind': request.registry.settings.auth_kind}


def setup(config):
    """Setup SAML2 auth - to be called when the app starts."""

    # Ensure python-lasso is available.
    if not lasso_loaded:
        raise Exception(
            'SAML2 enabled in settings but python-lasso could not be loaded.\n'
            'Download Lasso from <http://lasso.entrouvert.org/>.'
        )

    # Register the authentication policy.
    config.set_authentication_policy(AuthTktAuthenticationPolicy(
        config.get_settings()['saml2.auth_secret'],
        hashalg='sha512',
        callback=get_user_principals,
    ))

    # Add routes for SAML2 views.
    config.add_route('saml2_login', '/login')
    config.add_route('saml2_login_metadata', '/login_metadata')
    config.add_route('saml2_login_success', '/login_success')
    config.add_route('saml2_logout', '/logout')

    # Register SAML2 views. Avoid using the "view_config" decorator as we don't
    # want the views to be added when SAML2 is disabled.
    def add_view(view, **kwargs):
        config.add_view(
            view,
            permission=NO_PERMISSION_REQUIRED,
            http_cache=0,
            **kwargs
        )
    add_view(login_view, route_name='saml2_login', renderer='json')
    add_view(login_metadata_view, route_name='saml2_login_metadata')
    add_view(login_success_view, route_name='saml2_login_success')
    add_view(logout_view, route_name='saml2_logout', renderer='json')

    # The default 403 (forbidden) view produces HTML; change it to a JSON one.
    forbidden_view_config(renderer='json')(forbidden_view)
