from pyramid.view import view_config
from pyramid.renderers import get_renderer

from ..utils.xml_config import load_config
from ..models.models import DBSession
#from ..models.models import Role
#from ..models.models import Service
#from ..models.models import Emitter
from ..models.models import EventType
#from ..models.models import EventNodeRel
#from ..models.models import EmitterProfile
#from ..models.models import EmitterProfileEventTypeRel
#from ..models.models import EventNode


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
def home(request):
    res = get_base_res(request)
    res['view_title'] = 'Xbus Monitor Home'
    return res


@view_config(route_name='xml_config', request_method='GET',
             renderer='xbus.monitor:templates/xml_config.pt')
def config_get(request):
    res = get_base_res(request)
    res['view_title'] = 'Xbus Monitor xml config'
    return res


@view_config(route_name='xml_config', request_method='POST',
             renderer='xbus.monitor:templates/xml_config.pt')
def config_post(request):
    res = get_base_res(request)
    res['view_title'] = 'Xbus Monitor xml config'
    xml = request.POST['conftext']
    load_config(xml)
    return res


@view_config(route_name='event_config', request_method='GET',
             renderer='xbus.monitor:templates/event_config.pt')
def config_event_view_get(request):
    res = get_base_res(request)
    res['view_title'] = 'Xbus Monitor event config'

    query = DBSession.query(EventType)
    res['events'] = query.all()
    return res


@view_config(route_name='event_config_create', request_method='GET',
             renderer='xbus.monitor:templates/event_config_create.pt')
def config_event_create_get(request):
    res = get_base_res(request)
    res['view_title'] = 'Xbus Monitor event config create'
    return res


@view_config(route_name='event_config_create', request_method='POST',
             renderer='xbus.monitor:templates/event_config_create.pt')
def config_event_create_post(request):
    # Redirect to event_config
    res = get_base_res(request)
    res['view_title'] = 'Xbus Monitor event config create'
    return res


@view_config(route_name='event_config_edit', request_method='GET',
             renderer='xbus.monitor:templates/event_config_edit.pt')
def config_event_edit_get(request):
    res = get_base_res(request)
    res['view_title'] = 'Xbus Monitor event config edit'
    return res


@view_config(route_name='event_config_edit', request_method='POST',
             renderer='xbus.monitor:templates/event_config_edit.pt')
def config_event_edit_post(request):
    # Redirect to event_config
    res = get_base_res(request)
    res['view_title'] = 'Xbus Monitor event config edit'
    return res


@view_config(route_name='event_config_delete', request_method='POST')
def config_event_delete(request):
    # Redirect to event_config
    res = get_base_res(request)
    res['view_title'] = 'Xbus Monitor event config delete'
    return res
