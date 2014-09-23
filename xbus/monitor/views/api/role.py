from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPNotFound
from pyramid.response import Response
from pyramid.view import view_config
from sqlalchemy.exc import IntegrityError

from xbus.monitor.models.models import DBSession
from xbus.monitor.models.models import Role


@view_config(
    route_name='role_list',
    renderer='json',
)
def role_list(request):

    query = DBSession.query(Role)
    roles = query.all()
    jsonpload = {"roles": [role.as_dict() for role in roles]}
    return jsonpload


@view_config(
    route_name='role_create',
    renderer='json',
)
def role_create(request):

    record = Role()

    try:
        # Fill the record using received parameters.
        vals = request.json_body

        # TODO Implement.

    except (KeyError, ValueError):
        raise HTTPBadRequest(
            json_body={"error": "Invalid data"},
        )

    DBSession.add(record)
    DBSession.flush()
    DBSession.refresh(record)

    return record.as_dict()


def _get_record(request):
    if request.context is None:
        raise HTTPNotFound(
            json_body={
                "error": "Role ID {id} not found".format(
                    id=request.matchdict.get('id')
                )
            },
        )
    return request.context


@view_config(
    route_name='role',
    request_method='GET',
    renderer='json',
)
def role_read(request):
    record = _get_record(request)
    return record.as_dict()


@view_config(
    route_name='role',
    request_method='PUT',
    renderer='json',
)
def role_update(request):
    record = _get_record(request)

    try:
        # Fill the record using received parameters.
        vals = request.json_body

        record.name = vals['name']
        record.description = vals['description']

    except (KeyError, ValueError):
        raise HTTPBadRequest(
            json_body={"error": "Invalid data"},
        )

    try:
        DBSession.save(record)

    except IntegrityError:
        raise HTTPBadRequest(
            json_body={"error": "Duplicate names not allowed"},
        )

    return record.as_dict()


@view_config(
    route_name='role',
    request_method='DELETE',
    renderer='json',
)
def role_delete(request):
    record = _get_record(request)
    DBSession.delete(record)

    return Response(status_int=204, json_body={})