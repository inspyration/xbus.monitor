import base64
import datetime
from uuid import UUID as base_UUID

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref
from sqlalchemy.orm import mapper

from sqlalchemy.ext.declarative import declarative_base

from xbus.broker.model import emission_profile
from xbus.broker.model import emitter
from xbus.broker.model import emitter_profile
from xbus.broker.model import emitter_profile_event_type_rel
from xbus.broker.model import envelope
from xbus.broker.model import event
from xbus.broker.model import event_error
from xbus.broker.model import event_node
from xbus.broker.model import event_node_rel
from xbus.broker.model import event_type
from xbus.broker.model import input_descriptor
from xbus.broker.model import role
from xbus.broker.model import service
from xbus.broker.model.auth.main import user

from zope.sqlalchemy import ZopeTransactionExtension


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))


class BaseModel(object):

    _mapper = None

    @classmethod
    def get_mapper(cls):
        return cls._mapper

    @staticmethod
    def _serialize(value):
        """Serialize types JSON cannot handle."""

        # Base-64 encode binary data.
        if isinstance(value, bytes):
            return base64.b64encode(value).decode()

        if isinstance(value, datetime.date):
            return datetime.date.isoformat(value)

        if isinstance(value, datetime.datetime):
            return datetime.datetime.isoformat(value)

        if isinstance(value, base_UUID):
            return str(value)

        return value

    def as_dict(self):
        return {
            c.name: self._serialize(getattr(self, c.name))
            for c in self._mapper.c
        }


class Role(BaseModel):
    pass


class Service(BaseModel):
    pass


class Envelope(BaseModel):
    pass


class Event(BaseModel):
    pass


class EventError(BaseModel):
    pass


class EventType(BaseModel):
    pass


class EventNode(BaseModel):
    pass


class EmissionProfile(BaseModel):
    pass


class Emitter(BaseModel):
    pass


class EmitterProfile(BaseModel):
    pass


class InputDescriptor(BaseModel):
    pass


class User(BaseModel):
    pass


Role._mapper = mapper(Role, role, properties={
    'service': relationship(Service, backref=backref('roles', lazy="dynamic"))
})

Service._mapper = mapper(Service, service, properties={})

Envelope._mapper = mapper(Envelope, envelope, properties={
    'emitter': relationship(Emitter)
})

Event._mapper = mapper(Event, event, properties={
    'type': relationship(EventType),
    'emitter': relationship(Emitter),
    'envelope': relationship(
        Envelope, backref=backref('events', lazy="dynamic")
    )
})

EventError._mapper = mapper(EventError, event_error, properties={
    'event': relationship(Event)
})

EventType._mapper = mapper(EventType, event_type, properties={})

EventNode._mapper = mapper(EventNode, event_node, properties={
    'service': relationship(Service),
    'type': relationship(EventType, backref=backref('nodes', lazy="dynamic")),
    'children': relationship(
        EventNode, lazy='dynamic',
        secondary=event_node_rel,
        primaryjoin=event_node.c.id == event_node_rel.c.parent_id,
        secondaryjoin=event_node.c.id == event_node_rel.c.child_id,
        backref=backref('parents', lazy='dynamic')
    )
})

EmissionProfile._mapper = mapper(
    EmissionProfile, emission_profile, properties={
        'input_descriptor': relationship(InputDescriptor),
        'owner': relationship(User),
    }
)

Emitter._mapper = mapper(Emitter, emitter, properties={
    'profile': relationship(
        EmitterProfile, backref=backref('emitters', lazy='dynamic')
    )
})

EmitterProfile._mapper = mapper(EmitterProfile, emitter_profile, properties={
    'event_types': relationship(
        EventType, lazy='dynamic',
        secondary=emitter_profile_event_type_rel,
        backref=backref('emitter_profiles', lazy='dynamic')
    )
})

InputDescriptor._mapper = mapper(
    InputDescriptor, input_descriptor, properties={}
)


User._mapper = mapper(User, user, properties={})


Base = declarative_base()
