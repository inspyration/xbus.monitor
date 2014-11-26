from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from pyramid.view import view_config

from xbus.monitor.models.models import DBSession
from xbus.monitor.models.models import EmissionProfile

from .util import get_list


def _update_record(request, record):
    """Update the record using JSON data."""

    try:
        vals = request.json_body

        # TODO Handle input types and the fields they enable.
        record.input_descriptor_id = vals['input_descriptor_id']
        record.input_type = vals.get('input_type', 'descriptor')

        record.name = vals['name']

    except (KeyError, ValueError):
        raise HTTPBadRequest(
            json_body={"error": "Invalid data"},
        )


@view_config(
    route_name='emission_profile_list',
    renderer='json',
)
def emission_profile_list(request):
    return get_list(EmissionProfile, request.GET)


@view_config(
    route_name='emission_profile_create',
    renderer='json',
)
def emission_profile_create(request):

    record = EmissionProfile()

    _update_record(request, record)

    DBSession.add(record)
    DBSession.flush()
    DBSession.refresh(record)

    return record.as_dict()


def _get_record(request):
    if request.context is None:
        raise HTTPNotFound(
            json_body={
                "error": "Emission profile ID {id} not found".format(
                    id=request.matchdict.get('id')
                )
            },
        )
    return request.context


@view_config(
    route_name='emission_profile',
    request_method='GET',
    renderer='json',
)
def emission_profile_read(request):
    record = _get_record(request)
    return record.as_dict()


@view_config(
    route_name='emission_profile',
    request_method='PUT',
    renderer='json',
)
def emission_profile_update(request):
    record = _get_record(request)
    _update_record(request, record)
    return record.as_dict()


@view_config(
    route_name='emission_profile',
    request_method='DELETE',
    renderer='json',
)
def emission_profile_delete(request):
    record = _get_record(request)
    DBSession.delete(record)

    return Response(status_int=204, json_body={})
