from pyramid.view import view_config


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

    consumers = [
        {'id': 'abcd', 'name': 'consumer with clearing', 'clearing': True},
        {'id': 'efgh', 'name': 'consumer without clearing'},
    ]

    return [{'total_entries': len(consumers)}, consumers]
