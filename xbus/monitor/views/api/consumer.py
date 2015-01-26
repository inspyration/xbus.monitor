from pyramid.view import view_config

from xbus.monitor.consumers import get_consumers
from xbus.monitor.consumers import refresh_consumers


@view_config(
    route_name='consumer_list',
    request_method='GET',
    renderer='json',
    http_cache=0,
)
def consumer_list(request):
    """List consumers. They are not stored in the database.
    """

    refresh_consumers()

    consumers = get_consumers()
    return [{'total_entries': len(consumers)}, consumers]
