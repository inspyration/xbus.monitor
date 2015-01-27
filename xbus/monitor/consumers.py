"""Deal with Xbus consumers.

In particular, save those providing data clearing and the database they use.
"""

import aiozmq
from aiozmq import rpc
import asyncio
import logging
from pyramid.httpexceptions import HTTPBadRequest
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension

from xbus.monitor.models.monitor import DBSession
from xbus.monitor.models.monitor import Role


log = logging.getLogger(__name__)


def _make_session(db_url):
    """Build an SQLAlchemy session object from a database URL."""
    return scoped_session(sessionmaker(
        bind=create_engine(db_url),
        extension=ZopeTransactionExtension(),
    ))


# Store consumers and data clearing database URLs and 2 different arrays to
# make sure no database information is inadvertently leaked.

_consumers = []

# {consumer ID: SQLAlchemy session object to the data clearing database}
_consumer_clearing_sessions = {}


def get_consumers():
    return _consumers


def get_consumer_clearing_session(consumer_id):
    """Get an SQLAlchemy session object bound to the data clearing database
    provided by the specified consumer.

    :param consumer_id: UID of the Xbus consumer.
    :type consumer_id: String.

    :raise HTTPBadRequest.

    :rtype: sqlalchemy.orm.scoped_session.
    """

    if consumer_id:
        session = _consumer_clearing_sessions.get(consumer_id)
        if session:
            return session

    raise HTTPBadRequest(json_body={
        'error': 'Data clearing information missing.',
    })


@asyncio.coroutine
def _request_consumers(front_url, login, password, loop):
    """Ask Xbus for the list of consumers.

    @return Xbus consumers.
    @rtype List of dicts.
    """

    log.debug('Establishing RPC connection...')
    client = yield from rpc.connect_rpc(connect=front_url, loop=loop)
    log.debug('RPC connection OK')
    token = yield from client.call.login(login, password)
    log.debug('Got connection token: %s', token)

    consumers = yield from client.call.get_consumers(token)
    log.debug('Got the consumer list: %s', consumers)

    yield from client.call.logout(token)
    log.debug('Logged out; terminating')

    client.close()
    log.debug('Done.')

    return consumers


def refresh_consumers():
    """Ask Xbus for a fresh new list of Xbus consumers.
    """

    # Global arrays we are going to refresh.
    global _consumers
    global _consumer_clearing_sessions

    # TODO config params
    # The login & password must exist in the "emitter" database table.
    front_url = 'tcp://127.0.0.1:1984'
    login = 'upload_emitter'
    password = 'test'

    # Send our request via 0mq to the Xbus front-end.
    zmq_loop = aiozmq.ZmqEventLoopPolicy().new_event_loop()
    emitter = _request_consumers(front_url, login, password, zmq_loop)
    role_ids = zmq_loop.run_until_complete(emitter)

    # TODO Use the db to get info about roles? or just save role IDs?
    # TODO How to fetch data clearing information?

    session = DBSession()
    roles = session.query(Role).filter(Role.id.in_(role_ids))
    _consumers = [
        {
            'clearing': True,  # TODO Implement.
            'id': 'consumer-%d' % i,  # TODO Implement.
            'name': role.service.name,
        }
        for i, role in enumerate(roles)
    ]

    # Refresh the list of consumers with data clearing cache.
    # TODO Implement.
    data_clearing_db_url = (
        'postgresql://xbus:xbus@localhost:5432/xbus_clearinghouse'
    )
    _consumer_clearing_sessions = {
        'consumer-%d' % i: _make_session(data_clearing_db_url)
        for i, role in enumerate(roles)
        if data_clearing_db_url
    }
