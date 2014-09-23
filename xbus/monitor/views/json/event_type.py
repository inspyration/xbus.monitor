from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy.exc import IntegrityError

from xbus.monitor.models.models import DBSession
from xbus.monitor.models.models import EventType


@view_config(
    route_name='event_type_list',
    renderer='json',
)
def event_type_list(request):

    query = DBSession.query(EventType)
    events = query.all()
    jsonpload = {"events": [event.as_dict() for event in events]}
    return jsonpload


@view_config(
    route_name='event_type_create',
    renderer='json',
)
def event_type_create(request):

    # this is an eventtype creation asked by some user...
    et = EventType()

    try:
        vals = request.json_body

        # set event_type vals in accordance to payload
        et.name = vals['name']
        et.description = vals['description']

    except (KeyError, ValueError):
        raise HTTPBadRequest(
            json_body={"error": "Invalid data"},
        )

    try:
        DBSession.add(et)
        DBSession.flush()
        DBSession.refresh(et)

    except IntegrityError:
        # just in case the name is already in our database
        raise HTTPBadRequest(
            json_body={"error": "Duplicate names not allowed"},
        )

    return et.as_dict()


def _get_event_type(request):
    if request.context is None:
        raise HTTPNotFound(
            json_body={
                "error": "Event type ID {id} not found".format(
                    id=request.matchdict.get('id')
                )
            },
        )
    return request.context


@view_config(
    route_name='event_type',
    request_method='GET',
    renderer='json',
)
def event_type_read(request):
    event_type = _get_event_type(request)
    return event_type.as_dict()


@view_config(
    route_name='event_type',
    request_method='PUT',
    renderer='json',
)
def event_type_update(request):
    event_type = _get_event_type(request)

    try:
        vals = request.json_body

        # set event_type vals in accordance to payload
        event_type.name = vals['name']
        event_type.description = vals['description']

    except (KeyError, ValueError):
        raise HTTPBadRequest(
            json_body={"error": "Invalid data"},
        )

    DBSession.save(event_type)

    return event_type.as_dict()


@view_config(
    route_name='event_type',
    request_method='DELETE',
    renderer='json',
)
def event_type_delete(request):
    event_type = _get_event_type(request)
    DBSession.delete(event_type)

    return Response(status_int=204, json_body={})
