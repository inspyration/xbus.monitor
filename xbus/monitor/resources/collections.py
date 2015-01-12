from pyramid import security

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


class _GenericCollectionFactory(RootFactory):
    """Factory for collections of records; provides:
    - sqla_model: sqlalchemy class.
    """

    sqla_model = None  # To be overridden by derived classes.

    # Give any authenticated user full access to all models by default, unless
    # the ACL is specialized in the derived class.
    # TODO Wrong but easier for tests...
    __acl__ = [
        (security.Allow, security.Authenticated, 'create'),
        (security.Allow, security.Authenticated, 'read'),
        (security.Allow, security.Authenticated, 'update'),
        (security.Allow, security.Authenticated, 'delete'),
    ]


class CollectionFactory_emission_profile(_GenericCollectionFactory):
    sqla_model = EmissionProfile


class CollectionFactory_emitter(_GenericCollectionFactory):
    sqla_model = Emitter


class CollectionFactory_emitter_profile(_GenericCollectionFactory):
    sqla_model = EmitterProfile


class CollectionFactory_envelope(_GenericCollectionFactory):
    sqla_model = Envelope


class CollectionFactory_event(_GenericCollectionFactory):
    sqla_model = Event


class CollectionFactory_event_error(_GenericCollectionFactory):
    sqla_model = EventError


class CollectionFactory_event_error_tracking(_GenericCollectionFactory):
    sqla_model = EventErrorTracking


class CollectionFactory_event_node(_GenericCollectionFactory):
    sqla_model = EventNode


class CollectionFactory_event_type(_GenericCollectionFactory):
    sqla_model = EventType


class CollectionFactory_input_descriptor(_GenericCollectionFactory):
    sqla_model = InputDescriptor


class CollectionFactory_role(_GenericCollectionFactory):
    sqla_model = Role


class CollectionFactory_service(_GenericCollectionFactory):
    sqla_model = Service


class CollectionFactory_user(_GenericCollectionFactory):
    sqla_model = User
