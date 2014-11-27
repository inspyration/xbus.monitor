from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config

from xbus.monitor.models.models import EventError

from .util import get_list


@view_config(
    route_name='event_error_list',
    renderer='json',
)
def event_error_list(request):
    return get_list(EventError, request.GET)


def _get_record(request):
    if request.context.record is None:
        raise HTTPNotFound(
            json_body={
                "error": "Event error ID {id} not found".format(
                    id=request.matchdict.get('id')
                )
            },
        )
    return request.context.record


@view_config(
    route_name='event_error',
    request_method='GET',
    renderer='json',
)
def event_error_read(request):
    record = _get_record(request)
    return record.as_dict()
