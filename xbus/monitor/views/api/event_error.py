from xbus.monitor.models.models import EventError

from .util import get_list
from .util import get_record
from . import view_decorators


_MODEL = 'event_error'


@view_decorators.list(_MODEL)
def event_error_list(request):
    return get_list(EventError, request.GET)


@view_decorators.read(_MODEL)
def event_error_read(request):
    record = get_record(request, _MODEL)
    ret = record.as_dict()

    # Also include tracking items.
    ret['tracking'] = [tracker.id for tracker in record.tracking_list]

    return ret
