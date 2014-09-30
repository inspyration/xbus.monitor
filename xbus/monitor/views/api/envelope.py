from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from pyramid.view import view_config

from xbus.monitor.models.models import DBSession
from xbus.monitor.models.models import Envelope

from .util import get_list


def _update_record(request, record):
    """Update the record using JSON data."""

    try:
        vals = request.json_body

        record.emitter_id = vals['emitter_id']
        record.state = vals['state']
        record.posted_date = vals['posted_date']
        record.done_date = vals['done_date']

    except (KeyError, ValueError):
        raise HTTPBadRequest(
            json_body={"error": "Invalid data"},
        )


@view_config(
    route_name='envelope_list',
    renderer='json',
)
def envelope_list(request):
    return get_list('envelopes', Envelope)


@view_config(
    route_name='envelope_create',
    renderer='json',
)
def envelope_create(request):

    record = Envelope()

    _update_record(request, record)

    DBSession.add(record)
    DBSession.flush()
    DBSession.refresh(record)

    return record.as_dict()


def _get_record(request):
    if request.context is None:
        raise HTTPNotFound(
            json_body={
                "error": "Envelope ID {id} not found".format(
                    id=request.matchdict.get('id')
                )
            },
        )
    return request.context


@view_config(
    route_name='envelope',
    request_method='GET',
    renderer='json',
)
def envelope_read(request):
    record = _get_record(request)
    return record.as_dict()


@view_config(
    route_name='envelope',
    request_method='PUT',
    renderer='json',
)
def envelope_update(request):
    record = _get_record(request)
    _update_record(request, record)
    return record.as_dict()


@view_config(
    route_name='envelope',
    request_method='DELETE',
    renderer='json',
)
def envelope_delete(request):
    record = _get_record(request)
    DBSession.delete(record)

    return Response(status_int=204, json_body={})
