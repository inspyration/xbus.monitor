"""Deal with Xbus consumers.

In particular, save those providing data clearing and the database they use.
"""

from pyramid.httpexceptions import HTTPBadRequest
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension

# TODO Implement.


def _make_session(db_url):
    """Build an SQLAlchemy session object from a database URL."""
    return scoped_session(sessionmaker(
        bind=create_engine(db_url),
        extension=ZopeTransactionExtension(),
    ))


# Store consumers and data clearing database URLs and 2 different arrays to
# make sure no database information is inadvertently leaked.

_consumers = [
    {'id': 'abcd', 'name': 'consumer with clearing', 'clearing': True},
    {'id': 'efgh', 'name': 'consumer without clearing'},
]

# {consumer ID: SQLAlchemy session object to the data clearing database}
_consumer_clearing_sessions = {
    'abcd': _make_session(
        'postgresql://xbus:xbus@localhost:5432/xbus_clearinghouse'
    ),
}


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
