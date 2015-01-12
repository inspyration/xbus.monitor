from xbus.monitor.models.models import EventErrorTracking

from .util import get_list
from .util import get_record
from . import view_decorators


_MODEL = 'event_error_tracking'


@view_decorators.list(_MODEL)
def event_error_tracking_list(request):
    return get_list(EventErrorTracking, request.GET)


@view_decorators.read(_MODEL)
def event_error_tracking_read(request):
    record = get_record(request, _MODEL)
    return record.as_dict()
