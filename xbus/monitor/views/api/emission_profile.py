from pyramid.httpexceptions import HTTPBadRequest
from pyramid.response import Response

from xbus.monitor.auth import get_logged_user_id
from xbus.monitor.models.monitor import DBSession
from xbus.monitor.models.monitor import EmissionProfile

from .util import get_list
from .util import get_record
from . import view_decorators


_MODEL = 'emission_profile'


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


@view_decorators.list(_MODEL)
def emission_profile_list(request):
    # Only list the user's own emission profiles. Others can still be read (so
    # they can be accessed if they are referenced elsewhere) but they just
    # won't be listed here.
    ret = get_list(EmissionProfile, request.GET)
    return [ret[0], [
        item
        for item in ret[1]
        if item['owner_id'] == get_logged_user_id(request)
    ]]


@view_decorators.create(_MODEL)
def emission_profile_create(request):
    record = EmissionProfile()

    record.owner_id = get_logged_user_id(request)

    _update_record(request, record)

    DBSession.add(record)
    DBSession.flush()
    DBSession.refresh(record)

    return record.as_dict()


@view_decorators.read(_MODEL)
def emission_profile_read(request):
    record = get_record(request, _MODEL)
    return record.as_dict()


@view_decorators.update(_MODEL)
def emission_profile_update(request):
    record = get_record(request, _MODEL)
    _update_record(request, record)
    return record.as_dict()


@view_decorators.delete(_MODEL)
def emission_profile_delete(request):
    record = get_record(request, _MODEL)
    DBSession.delete(record)

    return Response(status_int=204, json_body={})
