from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from pyramid.view import view_config

from xbus.monitor.models.models import DBSession
from xbus.monitor.models.models import Emitter

from .util import get_list


def _update_record(request, record):
    """Update the record using JSON data."""

    try:
        vals = request.json_body

        record.login = vals['login']
        record.profile_id = vals['profile_id']
        record.last_emit = vals['last_emit']

    except (KeyError, ValueError):
        raise HTTPBadRequest(
            json_body={"error": "Invalid data"},
        )


@view_config(
    route_name='emitter_list',
    renderer='json',
)
def emitter_list(request):
    return get_list('emitters', Emitter)


@view_config(
    route_name='emitter_create',
    renderer='json',
)
def emitter_create(request):

    record = Emitter()

    _update_record(request, record)

    DBSession.add(record)
    DBSession.flush()
    DBSession.refresh(record)

    return record.as_dict()


def _get_record(request):
    if request.context is None:
        raise HTTPNotFound(
            json_body={
                "error": "Emitter ID {id} not found".format(
                    id=request.matchdict.get('id')
                )
            },
        )
    return request.context


@view_config(
    route_name='emitter',
    request_method='GET',
    renderer='json',
)
def emitter_read(request):
    record = _get_record(request)
    return record.as_dict()


@view_config(
    route_name='emitter',
    request_method='PUT',
    renderer='json',
)
def emitter_update(request):
    record = _get_record(request)
    _update_record(request, record)
    return record.as_dict()


@view_config(
    route_name='emitter',
    request_method='DELETE',
    renderer='json',
)
def emitter_delete(request):
    record = _get_record(request)
    DBSession.delete(record)

    return Response(status_int=204, json_body={})
