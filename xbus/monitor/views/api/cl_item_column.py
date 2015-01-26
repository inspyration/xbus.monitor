from pyramid.httpexceptions import HTTPBadRequest
from pyramid.response import Response

from xbus.monitor.models.data_clearing import DBSession
from xbus.monitor.models.data_clearing import ItemColumn

from .util import get_record
from . import view_decorators


_MODEL = 'cl_item_column'


def _update_record(request, record):
    """Update the record using JSON data."""

    try:
        vals = request.json_body

        record.type_id = vals['type_id']
        record.attribute_name = vals['attribute_name']
        record.field_name = vals['field_name']
        record.column_name = vals.get('column_name')
        record.display_name = vals.get('display_name')
        record.data_type = vals.get('data_type') or 'ANY'
        record.related_type_id = vals.get('related_type_id') or None
        record.join_id = vals.get('join_id') or None
        record.is_external_key = vals.get('is_external_key', False)
        record.is_clearable = vals.get('is_clearable', True)
        record.is_dest_default = vals.get('is_dest_default', False)
        record.is_protected = vals.get('is_protected', False)
        record.is_required = vals.get('is_required', False)

        if not record.column_name and (
            record.is_clearable or record.is_external_key
        ):
            raise HTTPBadRequest(
                json_body={
                    "error": "Must be associated with a database column"
                }
            )

    except (KeyError, ValueError):
        raise HTTPBadRequest(
            json_body={"error": "Invalid data"},
        )


@view_decorators.list(_MODEL)
def cl_item_column_list(request):

    # TODO Use util.get_list when clients represent relationship better (for
    # now, we just include the data they are going to need in the result list).

    def wrap_record(record):
        """Include type names."""
        ret = record.as_dict()
        ret['type_name'] = record.type.display_name
        return ret

    records = DBSession.query(ItemColumn).all()
    return [wrap_record(record) for record in records]


@view_decorators.create(_MODEL)
def cl_item_column_create(request):

    record = ItemColumn()

    _update_record(request, record)

    DBSession.add(record)
    DBSession.flush()
    DBSession.refresh(record)

    return record.as_dict()


@view_decorators.read(_MODEL)
def cl_item_column_read(request):
    record = get_record(request, _MODEL)
    return record.as_dict()


@view_decorators.update(_MODEL)
def cl_item_column_update(request):
    record = get_record(request, _MODEL)
    _update_record(request, record)
    return record.as_dict()


@view_decorators.delete(_MODEL)
def cl_item_column_delete(request):
    record = get_record(request, _MODEL)
    DBSession.delete(record)

    return Response(status_int=204, json_body={})

