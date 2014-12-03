"""Authorization management:
- Helpers to add and fetch principals.
"""

import logging
from pyramid import security


log = logging.getLogger(__name__)


# Principal prefixes.
_USER_PREFIX = 'user:'


# Default principals any logged user will posess.
_DEFAULT_PRINCIPALS = set((security.Everyone, security.Authenticated))


def user_principal(user_id):
    return '%s%s' % (_USER_PREFIX, user_id)


def get_user_principals(login, request=None):
    """Gather security groups for the specified user.
    @return Pyramid principal list.
    """

    log.debug('Fetching principals for the user %s', login)

    principals = _DEFAULT_PRINCIPALS.copy()

    # TODO Call xbus.broker.model.helpers.get_principals to fill the
    # "principals" set.

    # Record the ID of the user in principals.
    # TODO From the user db...
    user_id = '274627caada642d9b39091f0367c0199'
    if user_id:
        principals.add(user_principal(user_id))

    return list(principals)


def _get_logged_entities(request, security_prefix):
    """Find IDs of entities pointed to by principals starting with the
    specified prefix.
    """

    return [
        principal[len(security_prefix):]
        for principal in security.effective_principals(request)
        if principal.startswith(security_prefix)
    ]


def get_logged_user_id(request):
    return _get_logged_entities(request, _USER_PREFIX)[0]
