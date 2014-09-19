from pyramid.view import view_config
from pyramid.renderers import get_renderer
from pyramid.response import Response

from ..utils.xml_config import load_config
from ..models.models import DBSession
from ..models.models import EventType


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


@view_config(route_name='html_xml_config', request_method='GET',
             renderer='xbus.monitor:templates/xml_config.pt')
def config_get(request):
    res = get_base_res(request)
    res['view_title'] = 'Xbus Monitor xml config'
    return res


@view_config(route_name='html_xml_config', request_method='POST',
             renderer='xbus.monitor:templates/xml_config.pt')
def config_post(request):
    res = get_base_res(request)
    res['view_title'] = 'Xbus Monitor xml config'
    xml = request.POST['conftext']
    load_config(xml)
    return res


@view_config(route_name='html_event_config_list', request_method='GET',
             renderer='xbus.monitor:templates/event_config_list.pt')
def config_event_view_get(request):
    res = get_base_res(request)
    res['view_title'] = 'Xbus Monitor event config'
    query = DBSession.query(EventType)
    events = query.all()
    res['events'] = events
    return res


@view_config(route_name='html_event_config_create', request_method='GET',
             renderer='xbus.monitor:templates/event_config_create.pt')
def config_event_create_get(request):
    res = get_base_res(request)
    res['view_title'] = 'Xbus Monitor event config create'
    return res


@view_config(route_name='html_event_config_create', request_method='POST',
             renderer='xbus.monitor:templates/event_config_create.pt')
def config_event_create_post(request):
    # Redirect to event_config
    res = get_base_res(request)
    name = request.POST['name']
    description = request.POST['description']
    event = EventType(name=name, description=description)
    DBSession.add(event)
    DBSession.flush()
    request.response.status_int = 302
    request.response.location = '/html/config/event/{id}'.format(id=event.id)
    res['event'] = event
    res['view_title'] = 'Xbus Monitor event config create'
    return res


@view_config(route_name='html_event_config_read', request_method='GET',
             renderer='xbus.monitor:templates/event_config_read.pt')
def config_event_read(request):
    res = get_base_res(request)
    event_id = int(request.matchdict['id'])
    res['event'] = DBSession.query(EventType).get(event_id)
    res['view_title'] = 'Xbus Monitor event config'
    return res


@view_config(route_name='html_event_config_edit', request_method='GET',
             renderer='xbus.monitor:templates/event_config_edit.pt')
def config_event_edit_get(request):
    res = get_base_res(request)
    event_id = int(request.matchdict['id'])
    res['event'] = DBSession.query(EventType).get(event_id)
    res['view_title'] = 'Xbus Monitor event config edit'
    return res


@view_config(route_name='html_event_config_edit', request_method='POST',
             renderer='xbus.monitor:templates/event_config_edit.pt')
def config_event_edit_post(request):
    # Redirect to event_config
    res = get_base_res(request)
    event_id = int(request.matchdict['id'])
    event = DBSession.query(EventType).get(event_id)
    event.name = request.POST['name']
    event.description = request.POST['description']
    request.response.status_int = 302
    request.response.location = '/html/config/event/{id}'.format(id=event_id)
    res['event'] = event
    res['view_title'] = 'Xbus Monitor event config edit'
    return res


@view_config(route_name='html_event_config_delete', request_method='POST')
def config_event_delete(request):
    # Redirect to event_config
    res = get_base_res(request)
    event_id = int(request.matchdict['id'])
    DBSession.query(EventType).filter(EventType.id == event_id).delete()
    return Response("Redirecting to the event list...", status_int=302,
        content_type="text/plain", location='/html/config/event'
    )
