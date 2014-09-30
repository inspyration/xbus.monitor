import datetime
from uuid import uuid4
from uuid import UUID as base_UUID

from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    String,
    Text,
    DateTime,
    Enum,
    ForeignKey,
)

from .types import UUID

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship
)

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))


def serialize(value):
    """Serialize types JSON cannot handle."""

    if isinstance(value, datetime.date):
        return datetime.date.isoformat(value)

    if isinstance(value, datetime.datetime):
        return datetime.datetime.isoformat(value)

    if isinstance(value, base_UUID):
        return str(value)

    return value


def as_dict(obj):
    return {c.name: serialize(getattr(obj, c.name)) for c in obj.__table__.c}

Base = declarative_base()
Base.as_dict = as_dict


ENVELOPE_STATES = ['emit', 'canc', 'wait', 'exec', 'done', 'stop', 'fail']


class Role(Base):

    __tablename__ = 'role'

    service_fkey = ForeignKey('service.id', ondelete='CASCADE')

    id = Column(UUID, default=uuid4, primary_key=True)
    login = Column(String(length=64), index=True, nullable=False, unique=True)
    service_id = Column(UUID, service_fkey, index=True, nullable=False)
    last_logged = Column(DateTime)

    service = relationship('Service', backref='roles')


class RoleActive(Base):

    __tablename__ = 'role_active'

    role_fkey = ForeignKey('role.id', ondelete='CASCADE')

    role_id = Column(UUID, role_fkey, default=uuid4, primary_key=True)
    zmqid = Column(Integer, index=True, unique=True)
    ready = Column(Boolean, server_default='FALSE')
    last_act_date = Column(DateTime)

    role_data = relationship('Role', uselist=False, backref='activity_data')


class Service(Base):

    __tablename__ = 'service'

    id = Column(UUID, default=uuid4, primary_key=True)
    name = Column(String(length=64), index=True, unique=True)
    consumer = Column(Boolean, server_default='FALSE')
    description = Column(Text)


class Envelope(Base):

    __tablename__ = 'envelope'

    emitter_fkey = ForeignKey('emitter.id', ondelete='RESTRICT')
    state_enum = Enum(*ENVELOPE_STATES, name='envelope_state')

    id = Column(UUID, default=uuid4, primary_key=True)
    emitter_id = Column(UUID, emitter_fkey, nullable=False)
    state = Column(state_enum, nullable=False)
    posted_date = Column(DateTime, nullable=False)
    done_date = Column(DateTime)


class Event(Base):

    __tablename__ = 'event'

    envelope_fkey = ForeignKey('envelope.id', ondelete='CASCADE')
    emitter_fkey = ForeignKey('emitter.id', ondelete='RESTRICT')
    type_fkey = ForeignKey('event_type.id', ondelete='RESTRICT')

    id = Column(UUID, default=uuid4, primary_key=True)
    envelope_id = Column(UUID, envelope_fkey, index=True, nullable=False)
    emitter_id = Column(UUID, emitter_fkey, nullable=False)
    type_id = Column(UUID, type_fkey, nullable=False)
    started_date = Column(DateTime)
    done_date = Column(DateTime)
    estimated_items = Column(Integer)
    sent_items = Column(Integer)


class EventError(Base):

    __tablename__ = 'event_error'

    envelope_fkey = ForeignKey('envelope.id', ondelete='CASCADE')
    event_fkey = ForeignKey('event.id', ondelete='CASCADE')
    service_fkey = ForeignKey('service.id', ondelete='CASCADE')

    id = Column(UUID, default=uuid4, primary_key=True)
    envelope_id = Column(UUID, envelope_fkey, index=True, nullable=False)
    event_id = Column(UUID, event_fkey)
    service_id = Column(UUID, service_fkey)
    items = Column(Text)
    message = Column(Text)
    error_date = Column(DateTime, nullable=False)


class EventType(Base):

    __tablename__ = 'event_type'

    id = Column(UUID, default=uuid4, primary_key=True)
    name = Column(String(length=64), index=True, unique=True)
    description = Column(Text)


class EventNodeRel(Base):

    __tablename__ = 'event_node_rel'

    parent_fkey = ForeignKey('event_node.id', ondelete='CASCADE')
    child_fkey = ForeignKey('event_node.id', ondelete='CASCADE')

    parent_id = Column(UUID, parent_fkey, primary_key=True)
    child_id = Column(UUID, child_fkey, primary_key=True)


class EventNode(Base):

    __tablename__ = 'event_node'

    type_fkey = ForeignKey('event_type.id', ondelete='RESTRICT')
    service_fkey = ForeignKey('service.id', ondelete='RESTRICT')

    id = Column(UUID, default=uuid4, primary_key=True)
    service_id = Column(UUID, service_fkey, nullable=False)
    type_id = Column(UUID, type_fkey, index=True, nullable=False)
    start = Column(Boolean, server_default='FALSE')

    service = relationship('Service')
    type = relationship('EventType', backref='nodes')
    children = relationship(
        'EventNode',
        secondary=EventNodeRel.__table__,
        primaryjoin=id == EventNodeRel.parent_id,
        secondaryjoin=id == EventNodeRel.child_id,
        backref="parents"
    )


class Emitter(Base):

    __tablename__ = 'emitter'

    profile_fkey = ForeignKey('emitter_profile.id', ondelete='CASCADE')

    id = Column(UUID, default=uuid4, primary_key=True)
    login = Column(String(length=64), index=True, nullable=False, unique=True)
    profile_id = Column(UUID, profile_fkey, nullable=False)
    last_emit = Column(DateTime)

    profile = relationship('EmitterProfile', backref='emitters')


class EmitterProfileEventTypeRel(Base):

    __tablename__ = 'emitter_profile_event_type_rel'

    profile_fkey = ForeignKey('emitter_profile.id', ondelete='CASCADE')
    event_type_fkey = ForeignKey('event_type.id', ondelete='CASCADE')

    profile_id = Column(UUID, profile_fkey, primary_key=True)
    event_id = Column(UUID, event_type_fkey, primary_key=True)


class EmitterProfile(Base):

    __tablename__ = 'emitter_profile'

    id = Column(UUID, default=uuid4, primary_key=True)
    name = Column(String(length=64), index=True, nullable=False, unique=True)
    description = Column(Text)

    event_types = relationship(
        "EventType",
        secondary=EmitterProfileEventTypeRel.__table__,
        backref="emitter_profiles"
    )
