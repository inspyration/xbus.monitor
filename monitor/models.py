from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    String,
    Text,
    LargeBinary,
    DateTime,
    Enum,
    ForeignKey,
)

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
)

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

EVENT_STATE_ENUM = Enum("emit", "wait", "done", "fail", name="event_state")


class Role(Base):

    __tablename__ = 'role'

    id = Column(Integer, primary_key=True)
    login = Column(String(length=64), index=True, nullable=False, unique=True)
    last_logged = Column(DateTime)


class ActiveRole(Base):

    __tablename__ = 'role_active'

    role_fkey = ForeignKey('role.id', ondelete="CASCADE")

    role_id = Column(Integer, role_fkey, primary_key=True)
    zmqid = Column(Integer, index=True, unique=True)
    ready = Column(Boolean, server_default="FALSE")
    last_act_date = Column(DateTime)


class RoleServiceRel(Base):

    __tablename__ = 'role_service_rel'

    service_fkey = ForeignKey('service.id', ondelete="CASCADE")
    role_fkey = ForeignKey('role.id', ondelete="CASCADE")

    service_id = Column(Integer, service_fkey, primary_key=True)
    role_id = Column(Integer, role_fkey, primary_key=True)


class Service(Base):

    __tablename__ = 'service'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=64), index=True, unique=True)
    consumer = Column(Boolean, server_default="FALSE")


class Event(Base):

    __tablename__ = 'event'

    event_fkey = ForeignKey('event_type.id', ondelete="RESTRICT")

    id = Column(Integer, primary_key=True)
    type_id = Column(Integer, event_fkey, nullable=False)
    uuid = Column(LargeBinary(length=16), nullable=False)
    state = Column(EVENT_STATE_ENUM, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)


class EventType(Base):

    __tablename__ = 'event_type'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=64), index=True, unique=True)


class EventNode(Base):

    __tablename__ = 'event_node'

    event_fkey = ForeignKey('event_type.id', ondelete='RESTRICT')
    service_fkey = ForeignKey('service.id', ondelete='RESTRICT')

    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, service_fkey, nullable=False)
    event_id = Column(Integer, event_fkey, index=True, nullable=False)
    start = Column(Boolean, server_default="FALSE")


class EventNodeRel(Base):

    __tablename__ = 'event_node_rel'

    parent_fkey = ForeignKey('event_node.id', ondelete='CASCADE')
    child_fkey = ForeignKey('event_node.id', ondelete='CASCADE')

    parent_id = Column(Integer, parent_fkey, primary_key=True)
    child_id = Column(Integer, child_fkey, primary_key=True)


class MyModel(Base):

    __tablename__ = 'models'

    id = Column(Integer, primary_key=True)
    name = Column(Text)
    value = Column(Integer)
