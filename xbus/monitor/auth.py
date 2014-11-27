import logging
from pyramid import security


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
