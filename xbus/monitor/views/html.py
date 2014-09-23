from pyramid.renderers import get_renderer
from pyramid.view import view_config


def get_base_res(request):
    return {
        'context_url': request.path_qs,
        'project': 'xbus.monitor',
        'macros': (
            get_renderer('xbus.monitor:templates/base.pt')
            .implementation().macros
        ),
    }


@view_config(route_name='home', renderer='xbus.monitor:templates/home.pt')
def home_view(request):
    res = get_base_res(request)
    res['view_title'] = 'Home'
    return res


@view_config(
    route_name='xml_config_ui',
    renderer='xbus.monitor:templates/xml_config.pt',
)
def xml_config_view(request):
    res = get_base_res(request)
    res['view_title'] = 'XML configuration'
    return res
