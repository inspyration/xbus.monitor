import datetime
from uuid import uuid4
from uuid import UUID as base_UUID

from sqlalchemy import Binary
from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref
from sqlalchemy.orm import mapper

from sqlalchemy.ext.declarative import declarative_base

from xbus.broker.model import emitter
from xbus.broker.model import emitter_profile
from xbus.broker.model import emitter_profile_event_type_rel
from xbus.broker.model import envelope
from xbus.broker.model import event
from xbus.broker.model import event_error
from xbus.broker.model import event_node
from xbus.broker.model import event_node_rel
from xbus.broker.model import event_type
from xbus.broker.model import role
from xbus.broker.model import service

from zope.sqlalchemy import ZopeTransactionExtension

from .types import UUID

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))


class BaseModel(object):

    _mapper = None

    @classmethod
    def get_mapper(cls):
        return cls._mapper

    @staticmethod
    def _serialize(value):
        """Serialize types JSON cannot handle."""

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


class Emitter(BaseModel):
    pass


class EmitterProfile(BaseModel):
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


# Here follow non-Xbus-related models.
# TODO Move elsewhere?

Base = declarative_base()


class InputDescriptor(Base):
    """Store a descriptor used when sending data to Xbus."""

    __tablename__ = 'input_descriptor'

    id = Column(UUID, default=uuid4, primary_key=True)
    name = Column(String(length=64), index=True, nullable=False, unique=True)
    descriptor = Column(Binary)
