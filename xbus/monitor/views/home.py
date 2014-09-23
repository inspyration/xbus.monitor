from pyramid.view import view_config

from .util import get_view_params


@view_config(
    route_name='home',
    renderer='xbus.monitor:templates/home.pt',
)
def home_view(request):
    return get_view_params(request, 'Home')
