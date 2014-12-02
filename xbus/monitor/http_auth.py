import logging
from pyramid import security
import pyramid_httpauth


log = logging.getLogger(__name__)


# Default principals any logged user will posess.
DEFAULT_PRINCIPALS = set((security.Everyone, security.Authenticated))


def get_user_password(login):
    """Get the password of the specified user.
    Called by pyramid_httpauth.
    """

    # TODO Implement.

    return 'test'


def get_user_principals(login):
    """Gather security groups for the specified user.
    Called by pyramid_httpauth.
    @return Pyramid principal list.
    """

    log.debug('Fetching principals for the user %s', login)

    principals = DEFAULT_PRINCIPALS.copy()

    # TODO Call xbus.broker.model.helpers.get_principals to fill the
    # "principals" set.

    return list(principals)


def setup(config):
    """Setup HTTP auth - to be called when the app starts."""

    class Hacked_HttpAuthPolicy(pyramid_httpauth.HttpAuthPolicy):
        """Rename the "WWW-Authenticate" header of 401 HTTP responses so
        browsers ignore it but clients still get it, so they can provide their
        own auth form. Probably not entirely legit...
        """
        def login_required(self, request):
            ret = super(Hacked_HttpAuthPolicy, self).login_required(request)
            for index, header in enumerate(ret.headerlist):
                if header[0] == 'WWW-Authenticate':
                    header = list(header)
                    header[0] = 'X-WWW-Authenticate'
                    ret.headerlist[index] = tuple(header)
            return ret
    pyramid_httpauth.HttpAuthPolicy = Hacked_HttpAuthPolicy
