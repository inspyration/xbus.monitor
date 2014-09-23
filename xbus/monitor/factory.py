from pyramid.httpexceptions import HTTPBadRequest

from xbus.monitor.models.models import DBSession
from xbus.monitor.models.models import Emitter
from xbus.monitor.models.models import EmitterProfile
from xbus.monitor.models.models import Envelope
from xbus.monitor.models.models import Event
from xbus.monitor.models.models import EventError
from xbus.monitor.models.models import EventType
from xbus.monitor.models.models import Role
from xbus.monitor.models.models import RoleActive
from xbus.monitor.models.models import Service


def _get_record_id(request):
    try:
        return int(request.matchdict.get('id'))
    except:
        raise HTTPBadRequest(json_body={"error": "Invalid ID"})


def _generic_record_factory(request, sqla_model):
    record_id = _get_record_id(request)
    query = DBSession.query(sqla_model)
    query = query.filter(sqla_model.id == record_id)
    return query.first()


def emitter(request):
    return _generic_record_factory(request, Emitter)


def emitter_profile(request):
    return _generic_record_factory(request, EmitterProfile)


def envelope(request):
    return _generic_record_factory(request, Envelope)


def event(request):
    return _generic_record_factory(request, Event)


def event_error(request):
    return _generic_record_factory(request, EventError)


def event_type(request):
    return _generic_record_factory(request, EventType)


def role(request):
    return _generic_record_factory(request, Role)


def role_active(request):
    return _generic_record_factory(request, RoleActive)


def service(request):
    return _generic_record_factory(request, Service)
