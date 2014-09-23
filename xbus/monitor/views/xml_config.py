from pyramid.view import view_config

from .util import get_view_params


@view_config(
    route_name='xml_config_ui',
    renderer='xbus.monitor:templates/xml_config.pt',
)
def xml_config_view(request):
    return get_view_params(request, 'XML configuration')
