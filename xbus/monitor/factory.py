from xbus.monitor.models.models import DBSession
from xbus.monitor.models.models import EventType


def eventtype_factory(request):
    eventtype_id = request.matchdict.get('id')
    query = DBSession.query(EventType)
    query = query.filter(EventType.id == eventtype_id)
    return query.first()
