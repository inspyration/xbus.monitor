from pyramid import security

from xbus.monitor.auth import user_principal
from xbus.monitor.models.monitor import DBSession
from xbus.monitor.models.monitor import EmissionProfile
from xbus.monitor.models.monitor import Emitter
from xbus.monitor.models.monitor import EmitterProfile
from xbus.monitor.models.monitor import Envelope
from xbus.monitor.models.monitor import Event
from xbus.monitor.models.monitor import EventError
from xbus.monitor.models.monitor import EventErrorTracking
from xbus.monitor.models.monitor import EventNode
from xbus.monitor.models.monitor import EventTracking
from xbus.monitor.models.monitor import EventType
from xbus.monitor.models.monitor import InputDescriptor
from xbus.monitor.models.monitor import Role
from xbus.monitor.models.monitor import Service
from xbus.monitor.models.monitor import User
from xbus.monitor.resources.records import GenericRecordFactory


class _BaseRecordFactory(GenericRecordFactory):
    """Base class for record factories in this module."""

    def sqla_session(self, request):
        return DBSession


class RecordFactory_emission_profile(_BaseRecordFactory):
    sqla_model = EmissionProfile

    @property
    def __acl__(self):
        # Anyone can read but only owners can update / delete.
        owner_id = self.record.owner_id
        owner_principal = (
            user_principal(owner_id) if owner_id
            else security.Authenticated
        )
        return [
            (security.Allow, security.Authenticated, 'read'),
            (security.Allow, owner_principal, 'update'),
            (security.Allow, owner_principal, 'delete'),
        ]


class RecordFactory_emitter(_BaseRecordFactory):
    sqla_model = Emitter


class RecordFactory_emitter_profile(_BaseRecordFactory):
    sqla_model = EmitterProfile


class RecordFactory_envelope(_BaseRecordFactory):
    sqla_model = Envelope


class RecordFactory_event(_BaseRecordFactory):
    sqla_model = Event


class RecordFactory_event_error(_BaseRecordFactory):
    sqla_model = EventError


class RecordFactory_event_error_tracking(_BaseRecordFactory):
    sqla_model = EventErrorTracking


class RecordFactory_event_node(_BaseRecordFactory):
    sqla_model = EventNode


class RecordFactory_event_tracking(_BaseRecordFactory):
    sqla_model = EventTracking


class RecordFactory_event_type(_BaseRecordFactory):
    sqla_model = EventType


class RecordFactory_input_descriptor(_BaseRecordFactory):
    sqla_model = InputDescriptor


class RecordFactory_role(_BaseRecordFactory):
    sqla_model = Role


class RecordFactory_service(_BaseRecordFactory):
    sqla_model = Service


class RecordFactory_user(_BaseRecordFactory):
    id_attribute = 'user_id'
    sqla_model = User
