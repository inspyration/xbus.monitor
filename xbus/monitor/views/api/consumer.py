from pyramid.view import view_config

from xbus.monitor.consumers import get_consumers


@view_config(
    route_name='consumer_list',
    request_method='GET',
    renderer='json',
    http_cache=0,
)
def consumer_list(request):
    """List consumers. They are not stored in the database.
    """

    # TODO Implement.

    consumers = get_consumers()
    return [{'total_entries': len(consumers)}, consumers]
