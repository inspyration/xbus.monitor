from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy.exc import IntegrityError

from xbus.monitor.models.models import DBSession
from xbus.monitor.models.models import EventError

from .util import get_list


@view_config(
    route_name='event_error_list',
    renderer='json',
)
def event_error_list(request):
    return get_list('event_errors', EventError)


@view_config(
    route_name='event_error_create',
    renderer='json',
)
def event_error_create(request):

    record = EventError()

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
                "error": "Event error ID {id} not found".format(
                    id=request.matchdict.get('id')
                )
            },
        )
    return request.context


@view_config(
    route_name='event_error',
    request_method='GET',
    renderer='json',
)
def event_error_read(request):
    record = _get_record(request)
    return record.as_dict()


@view_config(
    route_name='event_error',
    request_method='PUT',
    renderer='json',
)
def event_error_update(request):
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

    except IntegrityError:
        raise HTTPBadRequest(
            json_body={"error": "Duplicate names not allowed"},
        )

    return record.as_dict()


@view_config(
    route_name='event_error',
    request_method='DELETE',
    renderer='json',
)
def event_error_delete(request):
    record = _get_record(request)
    DBSession.delete(record)

    return Response(status_int=204, json_body={})
