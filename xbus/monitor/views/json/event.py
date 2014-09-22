from pyramid.view import view_config
from pyramid.response import Response
from sqlalchemy.exc import IntegrityError

from xbus.monitor.models.models import DBSession
from xbus.monitor.models.models import EventType


@view_config(route_name='event_config_list', request_method='GET')
def config_event_list(request):

    query = DBSession.query(EventType)
    events = query.all()
    jsonpload = {"events": [event.as_dict() for event in events]}

    return Response(
        json_body=jsonpload, status_int=200, content_type="application/json"
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


@view_config(route_name='event_config_add', request_method='PUT')
def config_event_add(request):

    vals = request.json_body

    # this is an eventtype creation asked by some user...
    et = EventType()

    # set eventtype vals in accordance to payload
    et.name = vals['name']
    et.description = vals['description']

    try:
        DBSession.add(et)
        DBSession.flush()
        DBSession.refresh(et)

    except IntegrityError:
        # just in case the name is already in our database
        return Response(
            json_body={"error": "Duplicate names not allowed"},
            status_int=400,
            content_type="application/json",
        )

    return Response(
        json_body=et.as_dict(),
        status_int=200,
        content_type="application/json",
    )


@view_config(route_name='event_config', request_method='GET')
def config_event_read(request):

    if request.context is None:
        return Response(
            json_body={
                "error": "eventtype id {id} not found".format(
                    id=request.matchdict.get('id')
                )
            },
            status_int=404,
            content_type="application/json",
        )

    else:
        return Response(
            json_body=request.context.as_dict(),
            status_int=200,
            content_type="application/json",
        )


@view_config(route_name='event_config', request_method='POST')
def config_event_edit_post(request):

    eventtype = request.context

    if eventtype is None:
        return Response(status_int=404, content_type="application/json")

    vals = request.json_body
    # change eventtype vals in accordance to payload
    eventtype.name = vals['name']
    eventtype.description = vals['description']
    DBSession.save(eventtype)

    return Response(
        json_body=eventtype.as_dict(),
        status_int=200,
        content_type="application/json",
    )


@view_config(route_name='event_config', request_method='DELETE')
def config_event_delete(request):

    eventtype = request.context
    DBSession.delete(eventtype)

    return Response(status_int=204, content_type="application/json")
