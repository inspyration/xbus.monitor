from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy.exc import IntegrityError

from xbus.monitor.models.models import DBSession
from xbus.monitor.models.models import Envelope


@view_config(
    route_name='envelope_list',
    renderer='json',
)
def envelope_list(request):

    query = DBSession.query(Envelope)
    envelopes = query.all()
    jsonpload = {"envelopes": [envelope.as_dict() for envelope in envelopes]}
    return jsonpload


@view_config(
    route_name='envelope_create',
    renderer='json',
)
def envelope_create(request):

    record = Envelope()

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
    route_name='envelope',
    request_method='DELETE',
    renderer='json',
)
def envelope_delete(request):
    record = _get_record(request)
    DBSession.delete(record)

    return Response(status_int=204, json_body={})
