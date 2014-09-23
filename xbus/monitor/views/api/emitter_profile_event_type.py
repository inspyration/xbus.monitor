from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy.exc import IntegrityError

from xbus.monitor.models.models import DBSession
from xbus.monitor.models.models import EmitterProfileEventTypeRel

from .util import get_list


@view_config(
    route_name='emitter_profile_event_type_list',
    renderer='json',
)
def emitter_profile_event_type_list(request):
    return get_list('emitter_profile_event_types', EmitterProfileEventTypeRel)


@view_config(
    route_name='emitter_profile_event_type_create',
    renderer='json',
)
def emitter_profile_event_type_create(request):

    record = EmitterProfileEventTypeRel()

    try:
        # Fill the record using received parameters.
        vals = request.json_body

        # TODO Implement.

    except (KeyError, ValueError):
        raise HTTPBadRequest(
            json_body={"error": "Invalid data"},
        )

    DBSession.add(record)
    DBSession.flush()
    DBSession.refresh(record)

    return record.as_dict()


def _get_record(request):
    if request.context is None:
        raise HTTPNotFound(
            json_body={
                "error": "Emitter profile event type ID {id} not found".format(
                    id=request.matchdict.get('id')
                )
            },
        )
    return request.context


@view_config(
    route_name='emitter_profile_event_type',
    request_method='GET',
    renderer='json',
)
def emitter_profile_event_type_read(request):
    record = _get_record(request)
    return record.as_dict()


@view_config(
    route_name='emitter_profile_event_type',
    request_method='PUT',
    renderer='json',
)
def emitter_profile_event_type_update(request):
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
    route_name='emitter_profile_event_type',
    request_method='DELETE',
    renderer='json',
)
def emitter_profile_event_type_delete(request):
    record = _get_record(request)
    DBSession.delete(record)

    return Response(status_int=204, json_body={})
