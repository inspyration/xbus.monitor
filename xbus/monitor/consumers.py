"""Deal with Xbus consumers.

In particular, save those providing data clearing and the database they use.
"""

# TODO Implement.


# Store consumers and data clearing database URLs and 2 different arrays to
# make sure no database information is inadvertently leaked.

_consumers = [
    {'id': 'abcd', 'name': 'consumer with clearing', 'clearing': True},
    {'id': 'efgh', 'name': 'consumer without clearing'},
]

# {consumer ID: data clearing database URL}
_consumer_clearing_urls = {
    'abcd': 'postgresql://xbus:xbus@localhost:5432/xbus_clearinghouse',
}


def get_consumers():
    return _consumers


def get_consumer_clearing_url(consumer_id):
    return _consumer_clearing_urls[consumer_id]
