from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy.exc import IntegrityError

from xbus.monitor.models.models import DBSession
from xbus.monitor.models.models import EventNodeRel

from .util import get_list


@view_config(
    route_name='event_node_link_list',
    renderer='json',
)
def event_node_link_list(request):
    return get_list('event_node_links', EventNodeRel)


@view_config(
    route_name='event_node_link_create',
    renderer='json',
)
def event_node_link_create(request):

    record = EventNodeRel()

    try:
        # Fill the record using received parameters.
        vals = request.json_body

        record.name = vals['name']
        record.description = vals['description']

    except (KeyError, ValueError):
        raise HTTPBadRequest(
            json_body={"error": "Invalid data"},
        )

    try:
        DBSession.add(record)
        DBSession.flush()
        DBSession.refresh(record)

    except IntegrityError:
        raise HTTPBadRequest(
            json_body={"error": "Duplicate names not allowed"},
        )

    return record.as_dict()


def _get_record(request):
    if request.context is None:
        raise HTTPNotFound(
            json_body={
                "error": "Event node link ID {id} not found".format(
                    id=request.matchdict.get('id')
                )
            },
        )
    return request.context


@view_config(
    route_name='event_node_link',
    request_method='GET',
    renderer='json',
)
def event_node_link_read(request):
    record = _get_record(request)
    return record.as_dict()


@view_config(
    route_name='event_node_link',
    request_method='PUT',
    renderer='json',
)
def event_node_link_update(request):
    record = _get_record(request)

    try:
        # Fill the record using received parameters.
        vals = request.json_body

        record.name = vals['name']
        record.description = vals['description']

    except (KeyError, ValueError):
        raise HTTPBadRequest(
            json_body={"error": "Invalid data"},
        )

    try:
        DBSession.save(record)

    except IntegrityError:
        raise HTTPBadRequest(
            json_body={"error": "Duplicate names not allowed"},
        )

    return record.as_dict()


@view_config(
    route_name='event_node_link',
    request_method='DELETE',
    renderer='json',
)
def event_node_link_delete(request):
    record = _get_record(request)
    DBSession.delete(record)

    return Response(status_int=204, json_body={})
