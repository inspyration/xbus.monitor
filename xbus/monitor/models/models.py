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

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship
)

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()
ENVELOPE_STATES = ['emit', 'wait', 'exec', 'done', 'fail']


class Role(Base):

    __tablename__ = 'role'

    service_fkey = ForeignKey('service.id', ondelete='CASCADE')

    id = Column(Integer, primary_key=True)
    login = Column(String(length=64), index=True, nullable=False, unique=True)
    service_id = Column(Integer, service_fkey, index=True, nullable=False)
    last_logged = Column(DateTime)

    service = relationship("Service")


class ActiveRole(Base):

    __tablename__ = 'role_active'

    role_fkey = ForeignKey('role.id', ondelete='CASCADE')

    role_id = Column(Integer, role_fkey, primary_key=True)
    zmqid = Column(Integer, index=True, unique=True)
    ready = Column(Boolean, server_default='FALSE')
    last_act_date = Column(DateTime)


class Service(Base):

    __tablename__ = 'service'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=64), index=True, unique=True)
    consumer = Column(Boolean, server_default='FALSE')
    description = Column(Text)


class Emitter(Base):

    __tablename__ = 'emitter'

    profile_fkey = ForeignKey('emitter_profile.id', ondelete='CASCADE')

    id = Column(Integer, primary_key=True)
    login = Column(String(length=64), index=True, nullable=False, unique=True)
    profile_id = Column(Integer, profile_fkey, nullable=False)
    last_emit = Column(DateTime)


class EmitterProfile(Base):

    __tablename__ = 'emitter_profile'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=64), index=True, nullable=False, unique=True)
    description = Column(Text)


class EmitterProfileEventTypeRel(Base):

    __tablename__ = 'emitter_profile_event_type_rel'

    profile_fkey = ForeignKey('emitter_profile.id', ondelete='CASCADE')
    event_type_fkey = ForeignKey('event_type.id', ondelete='CASCADE')

    profile_id = Column(Integer, profile_fkey, primary_key=True)
    event_id = Column(Integer, event_type_fkey, primary_key=True)


class Envelope(Base):

    __tablename__ = 'envelope'

    emitter_fkey = ForeignKey('emitter.id', ondelete='RESTRICT')
    state_enum = Enum(*ENVELOPE_STATES, name='envelope_state')

    uuid = Column(UUID, primary_key=True)
    emitter_id = Column(Integer, emitter_fkey, nullable=False)
    state = Column(state_enum, nullable=False)
    posted_date = Column(DateTime, nullable=False)
    done_date = Column(DateTime)


class Event(Base):

    __tablename__ = 'event'

    envelope_fkey = ForeignKey('envelope.uuid', ondelete='CASCADE')
    emitter_fkey = ForeignKey('emitter.id', ondelete='RESTRICT')
    type_fkey = ForeignKey('event_type.id', ondelete='RESTRICT')

    uuid = Column(UUID, primary_key=True)
    envelope_uuid = Column(UUID, envelope_fkey, index=True, nullable=False)
    emitter_id = Column(Integer, emitter_fkey, nullable=False)
    type_id = Column(Integer, type_fkey, nullable=False)
    started_date = Column(DateTime)
    done_date = Column(DateTime)


class EventError(Base):

    __tablename__ = 'event_error'

    envelope_fkey = ForeignKey('envelope.uuid', ondelete='CASCADE')
    event_fkey = ForeignKey('event.uuid', ondelete='CASCADE')
    service_fkey = ForeignKey('service.id', ondelete='CASCADE')

    id = Column(Integer, primary_key=True)
    envelope_uuid = Column(UUID, envelope_fkey, index=True, nullable=False)
    event_uuid = Column(UUID, event_fkey, nullable=False)
    service_id = Column(Integer, service_fkey)
    items = Column(Text)
    message = Column(Text)
    error_date = Column(DateTime, nullable=False)


class EventType(Base):

    __tablename__ = 'event_type'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=64), index=True, unique=True)
    description = Column(Text)

    nodes = relationship("EventNode")


class EventNode(Base):

    __tablename__ = 'event_node'

    type_fkey = ForeignKey('event_type.id', ondelete='RESTRICT')
    service_fkey = ForeignKey('service.id', ondelete='RESTRICT')

    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, service_fkey, nullable=False)
    type_id = Column(Integer, type_fkey, index=True, nullable=False)
    start = Column(Boolean, server_default='FALSE')


class EventNodeRel(Base):

    __tablename__ = 'event_node_rel'

    parent_fkey = ForeignKey('event_node.id', ondelete='CASCADE')
    child_fkey = ForeignKey('event_node.id', ondelete='CASCADE')

    parent_id = Column(Integer, parent_fkey, primary_key=True)
    child_id = Column(Integer, child_fkey, primary_key=True)
