from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from pyramid.view import view_config

from xbus.monitor.models.models import DBSession
from xbus.monitor.models.models import EventNode

from .util import get_list


def _update_record(request, record):
    """Update the record using JSON data."""

    try:
        vals = request.json_body

        record.service_id = vals['service_id']
        record.type_id = vals['type_id']
        record.is_start = vals.get('is_start', False)

    except (KeyError, ValueError):
        raise HTTPBadRequest(
            json_body={"error": "Invalid data"},
        )


@view_config(
    route_name='event_node_list',
    renderer='json',
)
def event_node_list(request):
    return get_list(EventNode, request.GET)


@view_config(
    route_name='event_node_create',
    renderer='json',
)
def event_node_create(request):

    record = EventNode()

    _update_record(request, record)

    DBSession.add(record)
    DBSession.flush()
    DBSession.refresh(record)

    return record.as_dict()


def _get_record(request):
    if request.context.record is None:
        raise HTTPNotFound(
            json_body={
                "error": "Event node ID {id} not found".format(
                    id=request.matchdict.get('id')
                )
            },
        )
    return request.context.record


@view_config(
    route_name='event_node',
    request_method='GET',
    renderer='json',
)
def event_node_read(request):
    record = _get_record(request)
    return record.as_dict()


@view_config(
    route_name='event_node',
    request_method='PUT',
    renderer='json',
)
def event_node_update(request):
    record = _get_record(request)
    _update_record(request, record)
    return record.as_dict()


@view_config(
    route_name='event_node',
    request_method='DELETE',
    renderer='json',
)
def event_node_delete(request):
    record = _get_record(request)
    DBSession.delete(record)

    return Response(status_int=204, json_body={})


@view_config(
    route_name='event_node_rel',
    request_method='PUT',
    renderer='json',
)
def event_node_rel_add(request):

    record = _get_record(request)
    rel_name, rid = request.matchdict.get('rel'), request.matchdict.get('rid')
    rel = record.get_mapper().get_property(rel_name)
    rel_list = getattr(record, rel_name, None)
    if rel is None or rel_list is None or not hasattr(rel_list, 'append'):
        raise HTTPBadRequest(
            json_body={
                "error": "Relationship {} does not exist".format(rel_name)
            },
        )

    query = DBSession.query(rel.mapper)
    added_record = query.get(rid)
    if added_record is None:
        raise HTTPNotFound(
            json_body={"error": "Event node ID {id} not found".format(id=rid)},
        )
    if added_record not in rel_list:
        rel_list.append(added_record)
    else:
        raise HTTPBadRequest(
            json_body={"error": "Object is already in the relationship"},
        )
    return added_record.as_dict()


@view_config(
    route_name='event_node_rel',
    request_method='DELETE',
    renderer='json',
)
def event_node_rel_remove(request):

    record = _get_record(request)
    rel_name, rid = request.matchdict.get('rel'), request.matchdict.get('rid')
    rel = record.get_mapper().get_property(rel_name)
    rel_list = getattr(record, rel_name, None)
    if rel is None or rel_list is None or not hasattr(rel_list, 'append'):
        raise HTTPBadRequest(
            json_body={
                "error": "Relationship {} does not exist".format(rel_name)
            },
        )

    query = DBSession.query(rel.mapper)
    removed_record = query.get(rid)
    if removed_record is None:
        raise HTTPNotFound(
            json_body={"error": "Event node ID {id} not found".format(id=rid)},
        )
    if removed_record in rel_list:
        rel_list.remove(removed_record)
    else:
        raise HTTPBadRequest(
            json_body={"error": "Object is not in the relationship"},
        )
    return Response(status_int=204, json_body={})


@view_config(
    route_name='event_node_rel_list',
    renderer='json',
)
def event_node_rel_list(request):

    record = _get_record(request)
    rel_name = request.matchdict.get('rel')
    rel = record.get_mapper().get_property(rel_name)
    rel_list = getattr(record, rel_name, None)
    if rel is None or rel_list is None or not hasattr(rel_list, 'filter'):
        raise HTTPBadRequest(
            json_body={
                "error": "Relationship {} does not exist".format(rel_name)
            },
        )

    return get_list(rel.mapper, request.GET, rel_list)


@view_config(
    route_name='event_node_rel_create',
    renderer='json',
)
def event_node_rel_create(request):

    record = _get_record(request)
    rel_name = request.matchdict.get('rel')
    rel = record.get_mapper().get_property(rel_name)
    rel_list = getattr(record, rel_name, None)
    if rel is None or rel_list is None or not hasattr(rel_list, 'filter'):
        raise HTTPBadRequest(
            json_body={
                "error": "Relationship {} does not exist".format(rel_name)
            },
        )

    created_record = rel.mapper.entity(**request.json_body)
    rel_list.append(created_record)
    return created_record.as_dict()
