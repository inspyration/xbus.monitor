from pyramid.httpexceptions import HTTPBadRequest

from xbus.monitor.models.models import DBSession
from xbus.monitor.models.models import EventType


def _get_record_id(request):
    try:
        return int(request.matchdict.get('id'))
    except:
        raise HTTPBadRequest(json_body={"error": "Invalid ID"})


def event_type(request):
    record_id = _get_record_id(request)
    query = DBSession.query(EventType)
    query = query.filter(EventType.id == record_id)
    return query.first()
