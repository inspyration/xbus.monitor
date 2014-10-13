from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from pyramid.view import view_config

from xbus.monitor.models.models import DBSession
from xbus.monitor.models.models import RoleActive

from .util import get_list


def _update_record(request, record):
    """Update the record using JSON data."""

    try:
        vals = request.json_body

        record.role_id = vals['role_id']
        record.zmqid = vals['zmqid']
        record.ready = vals.get('ready', False)
        record.last_act_date = vals['last_act_date']

    except (KeyError, ValueError):
        raise HTTPBadRequest(
            json_body={"error": "Invalid data"},
        )


@view_config(
    route_name='role_active_list',
    renderer='json',
)
def role_active_list(request):
    return get_list(RoleActive, request.GET)


@view_config(
    route_name='role_active_create',
    renderer='json',
)
def role_active_create(request):

    record = RoleActive()

    _update_record(request, record)

    DBSession.add(record)
    DBSession.flush()
    DBSession.refresh(record)

    return record.as_dict()


def _get_record(request):
    if request.context is None:
        raise HTTPNotFound(
            json_body={
                "error": "Active role ID {id} not found".format(
                    id=request.matchdict.get('id')
                )
            },
        )
    return request.context


@view_config(
    route_name='role_active',
    request_method='GET',
    renderer='json',
)
def role_active_read(request):
    record = _get_record(request)
    return record.as_dict()


@view_config(
    route_name='role_active',
    request_method='PUT',
    renderer='json',
)
def role_active_update(request):
    record = _get_record(request)
    _update_record(request, record)
    return record.as_dict()


@view_config(
    route_name='role_active',
    request_method='DELETE',
    renderer='json',
)
def role_active_delete(request):
    record = _get_record(request)
    DBSession.delete(record)

    return Response(status_int=204, json_body={})
