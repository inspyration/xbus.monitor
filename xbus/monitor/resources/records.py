from pyramid.httpexceptions import HTTPBadRequest

from xbus.monitor.models.models import DBSession
from xbus.monitor.models.models import EmissionProfile
from xbus.monitor.models.models import Emitter
from xbus.monitor.models.models import EmitterProfile
from xbus.monitor.models.models import Envelope
from xbus.monitor.models.models import Event
from xbus.monitor.models.models import EventError
from xbus.monitor.models.models import EventNode
from xbus.monitor.models.models import EventType
from xbus.monitor.models.models import InputDescriptor
from xbus.monitor.models.models import Role
from xbus.monitor.models.models import Service
from xbus.monitor.resources.root import RootFactory


class _GenericRecordFactory(RootFactory):
    """Factory for individual records; provides:
    - record_id.
    - record: sqlalchemy representation of the record.
    - sqla_model: sqlalchemy class.
    """

    sqla_model = None  # To be overridden by derived classes.

    def __init__(self, request):
        self.record_id = self._get_record_id(request)
        query = DBSession.query(self.sqla_model)
        query = query.filter(self.sqla_model.id == self.record_id)
        self.record = query.first()

    @staticmethod
    def _get_record_id(request):
        try:
            return request.matchdict.get('id')
        except:
            raise HTTPBadRequest(json_body={"error": "Invalid ID"})


class RecordFactory_emission_profile(_GenericRecordFactory):
    sqla_model = EmissionProfile


class RecordFactory_emitter(_GenericRecordFactory):
    sqla_model = Emitter


class RecordFactory_emitter_profile(_GenericRecordFactory):
    sqla_model = EmitterProfile


class RecordFactory_envelope(_GenericRecordFactory):
    sqla_model = Envelope


class RecordFactory_event(_GenericRecordFactory):
    sqla_model = Event


class RecordFactory_event_error(_GenericRecordFactory):
    sqla_model = EventError


class RecordFactory_event_node(_GenericRecordFactory):
    sqla_model = EventNode


class RecordFactory_event_type(_GenericRecordFactory):
    sqla_model = EventType


class RecordFactory_input_descriptor(_GenericRecordFactory):
    sqla_model = InputDescriptor


class RecordFactory_role(_GenericRecordFactory):
    sqla_model = Role


class RecordFactory_service(_GenericRecordFactory):
    sqla_model = Service
