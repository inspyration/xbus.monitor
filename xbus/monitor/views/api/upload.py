from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPNotImplemented
from pyramid.view import view_config


@view_config(
    route_name='upload',
    request_method='POST',
    renderer='json',
)
def upload(request):
    """View to handle file uploads. They are sent to Xbus.
    """

    emission_profile_id = request.params.get('emission_profile_id')
    if not emission_profile_id:
        raise HTTPBadRequest(
            json_body={'error': 'No emission profile selected'},
        )

    file = request.params.get('file')

    # TODO Implement.
    import pdb
    pdb.set_trace()
    raise HTTPNotImplemented()
