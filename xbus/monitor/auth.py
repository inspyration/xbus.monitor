"""Authorization management:
- Helpers to add and fetch principals.
"""

import logging
from pyramid import security

from xbus.monitor.models.models import DBSession
from xbus.monitor.models.models import User


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

    db_session = DBSession()

    user = db_session.query(User).filter(User.user_name == login).first()
    if not user:
        return principals

    # Record the ID of the user in principals.
    principals.add(user_principal(user.user_id))

    # Add actual principals.
    # TODO Probably a better way with joins / model declaration setup...
    principals.update(
        permission.permission_name
        for group in user.group_list
        for permission in group.permission_list
    )

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
