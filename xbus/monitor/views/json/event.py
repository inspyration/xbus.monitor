from pyramid.view import view_config
from pyramid.renderers import get_renderer
from pyramid.response import Response

from ...utils.xml_config import load_config
from ...models.models import DBSession
from ...models.models import EventType


@view_config(route_name='event_config_list', request_method='GET')
def config_event_list(request):

    query = DBSession.query(EventType)
    events = query.all()
    event_dicts = [event.as_dict() for event in events]

    return Response(
        json_body=event_dicts, status_int=200, content_type="application/json"
    )


@view_config(route_name='event_config_list', request_method='POST')
def config_event_post(request):

    vals = request.json_body

    name = vals['name']
    description = vals['description']
    event = EventType(name=name, description=description)
    DBSession.add(event)
    DBSession.flush()
    event_dict = event.as_dict()

    return Response(
        json_body=event_dict, status_int=201, content_type="application/json",
        location='/config/event/{id}'.format(id=event.id)
    )


@view_config(route_name='event_config', request_method='GET')
def config_event_read(request):

    event_id = int(request.matchdict['id'])

    query = DBSession.query(EventType)
    event = query.get(event_id)
    if event is None:
        return Response(status_int=404, content_type="application/json")
    event_dict = event.as_dict()

    return Response(
        json_body=event_dict, status_int=200, content_type="application/json"
    )


@view_config(route_name='event_config', request_method='POST')
def config_event_edit_post(request):

    event_id = int(request.matchdict['id'])
    vals = request.json_body

    query = DBSession.query(EventType)
    event = query.get(event_id)
    if event is None:
        return Response(status_int=404, content_type="application/json")
    event.name = vals['name']
    event.description = vals['description']
    event_dict = event.as_dict()

    return Response(
        json_body=event_dict, status_int=200, content_type="application/json"
    )


@view_config(route_name='event_config', request_method='DELETE')
def config_event_delete(request):

    event_id = int(request.matchdict['id'])

    query = DBSession.query(EventType).filter(EventType.id == event_id)
    rows = query.delete()
    if rows == 0:
        return Response(status_int=404, content_type="application/json")

    return Response(status_int=204, content_type="application/json")
