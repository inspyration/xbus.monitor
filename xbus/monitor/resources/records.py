from pyramid.httpexceptions import HTTPBadRequest
from pyramid import security

from xbus.monitor.auth import user_principal
from xbus.monitor.models.models import DBSession
from xbus.monitor.models.models import EmissionProfile
from xbus.monitor.models.models import Emitter
from xbus.monitor.models.models import EmitterProfile
from xbus.monitor.models.models import Envelope
from xbus.monitor.models.models import Event
from xbus.monitor.models.models import EventError
from xbus.monitor.models.models import EventErrorTracking
from xbus.monitor.models.models import EventNode
from xbus.monitor.models.models import EventType
from xbus.monitor.models.models import InputDescriptor
from xbus.monitor.models.models import Role
from xbus.monitor.models.models import Service
from xbus.monitor.models.models import User
from xbus.monitor.resources.root import RootFactory


class _GenericRecordFactory(RootFactory):
    """Factory for individual records; provides:
    - id_attribute: name of the "ID" attribute.
    - record_id.
    - record: sqlalchemy representation of the record.
    - sqla_model: sqlalchemy class.
    """

    id_attribute = 'id'  # May be overridden by derived classes.
    sqla_model = None  # To be overridden by derived classes.

    # Give any authenticated user full access to all models by default, unless
    # the ACL is specialized in the derived class.
    # TODO Wrong but easier for tests...
    __acl__ = [
        (security.Allow, security.Authenticated, 'read'),
        (security.Allow, security.Authenticated, 'update'),
        (security.Allow, security.Authenticated, 'delete'),
    ]

    def __init__(self, request):
        self.record_id = self._get_record_id(request)
        query = DBSession.query(self.sqla_model)
        query = query.filter(
            getattr(self.sqla_model, self.id_attribute) == self.record_id
        )
        self.record = query.first()

    @staticmethod
    def _get_record_id(request):
        try:
            return request.matchdict.get('id')
        except:
            raise HTTPBadRequest(json_body={"error": "Invalid ID"})


class RecordFactory_emission_profile(_GenericRecordFactory):
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


class RecordFactory_event_error_tracking(_GenericRecordFactory):
    sqla_model = EventErrorTracking


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


class RecordFactory_user(_GenericRecordFactory):
    id_attribute = 'user_id'
    sqla_model = User
