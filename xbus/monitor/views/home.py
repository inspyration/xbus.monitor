from pyramid.view import view_config

from xbus.monitor.i18n import req_l10n

from .util import get_view_params


@view_config(
    route_name='home',
    renderer='xbus.monitor:templates/home.pt',
)
def home_view(request):
    _ = req_l10n(request)
    return get_view_params(request, _('Home'))
