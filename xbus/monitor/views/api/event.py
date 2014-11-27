from pyramid.httpexceptions import HTTPNotFound
from pyramid.view import view_config

from xbus.monitor.models.models import Event

from .util import get_list


@view_config(
    route_name='event_list',
    renderer='json',
)
def event_list(request):
    return get_list(Event, request.GET)


def _get_record(request):
    if request.context.record is None:
        raise HTTPNotFound(
            json_body={
                "error": "Event ID {id} not found".format(
                    id=request.matchdict.get('id')
                )
            },
        )
    return request.context.record


@view_config(
    route_name='event',
    request_method='GET',
    renderer='json',
)
def event_read(request):
    record = _get_record(request)
    return record.as_dict()
