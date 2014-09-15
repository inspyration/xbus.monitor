from pyramid.view import view_config
from sqlalchemy.exc import DBAPIError
from xml.etree import ElementTree

from .models import (
    DBSession,
    Role,
    Service,
    Emitter,
    EmitterProfile,
    EmitterProfileEventTypeRel,
    EventType,
    EventNode,
    EventNodeRel
)


@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    return {'project': 'monitor'}


@view_config(route_name='xml_config', request_method='GET', renderer='templates/xml_config.pt')
def config_get(request):
    return {}


@view_config(route_name='xml_config', request_method='POST', renderer='templates/xml_config.pt')
def config_post(request):
    root = ElementTree.fromstring(request.POST['conftext'])
    session = DBSession()
    for service in root.findall('service'):
        name = service.get('name')
        consumer = service.get('consumer', False)
        s = Service(name=name, consumer=consumer, description=service.text)
        session.add(s)


@view_config(route_name='event_config', request_method='GET', renderer='templates/event_config.pt')
def config_event_view_get(request):
    events = DBSession.query(EventType).add_columns('name', 'description').all()
    print events
    return {'events': events}


@view_config(route_name='event_config_create', request_method='GET', renderer='templates/event_config_create.pt')
def config_event_create_get(request):
    return {}


@view_config(route_name='event_config_create', request_method='POST', renderer='templates/event_config_create.pt')
def config_event_create_post(request):
    # Redirect to event_config
    return {}


@view_config(route_name='event_config_edit', request_method='GET', renderer='templates/event_config_edit.pt')
def config_event_edit_get(request):
    return {}


@view_config(route_name='event_config_edit', request_method='POST', renderer='templates/event_config_edit.pt')
def config_event_edit_post(request):
    # Redirect to event_config
    return {}


@view_config(route_name='event_config_delete', request_method='POST')
def config_event_delete(request):
    # Redirect to event_config
    return {}
