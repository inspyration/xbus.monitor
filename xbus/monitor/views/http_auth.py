from pyramid.security import NO_PERMISSION_REQUIRED
import pyramid_httpauth

from xbus.monitor.models.models import DBSession
from xbus.monitor.models.models import User


def login_view(request):
    """Nothing special for HTTP auth - let the client handle this."""
    return {'auth_kind': request.registry.settings.auth_kind}


def logout_view(request):
    """Just empty the session and let the client handle this."""
    request.session.clear()
    return {'auth_kind': request.registry.settings.auth_kind}


def setup(config):
    """Setup HTTP auth - to be called when the app starts."""

    class Hacked_HttpAuthPolicy(pyramid_httpauth.HttpAuthPolicy):
        def authenticated_userid(self, request):
            """Override to change the password verifier (we don't store them as
            clear text).
            """

            login = self.unauthenticated_userid(request)
            password = self.get_password(request)

            db_session = DBSession()

            user = db_session.query(User).filter(
                User.user_name == login
            ).first()
            if not user:
                return None

            # TODO Does not work - use helpers from sbus.monitor.
            return user.password == password

        def login_required(self, request):
            """Rename the "WWW-Authenticate" header of 401 HTTP responses so
            browsers ignore it but clients still get it, so they can provide
            their own auth form. Probably not entirely legit...
            """

            ret = super(Hacked_HttpAuthPolicy, self).login_required(request)
            for index, header in enumerate(ret.headerlist):
                if header[0] == 'WWW-Authenticate':
                    header = list(header)
                    header[0] = 'X-WWW-Authenticate'
                    ret.headerlist[index] = tuple(header)
            return ret

    pyramid_httpauth.HttpAuthPolicy = Hacked_HttpAuthPolicy

    # Add routes for HTTP auth views.
    config.add_route('httpauth_login', '/login')
    config.add_route('httpauth_logout', '/logout')

    # Register HTTP auth views. Avoid using the "view_config" decorator as we
    # don't want the views to be added when HTTP auth is disabled.
    def add_view(view, **kwargs):
        config.add_view(
            view,
            permission=NO_PERMISSION_REQUIRED,
            http_cache=0,
            renderer='json',
            **kwargs
        )
    add_view(login_view, route_name='httpauth_login')
    add_view(logout_view, route_name='httpauth_logout')
