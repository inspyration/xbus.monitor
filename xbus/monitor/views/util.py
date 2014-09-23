from pyramid import security
from pyramid.renderers import get_renderer


def get_view_params(request, title):
    """Fill parameters used by every view."""

    login = security.authenticated_userid(request)

    return {
        'context_url': request.path_qs,
        'login': login,
        'macros': (
            get_renderer('xbus.monitor:templates/base.pt')
            .implementation().macros
        ),
        'project': 'XBus monitor',
        'view_title': title,
    }
