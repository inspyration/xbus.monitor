from pyramid.httpexceptions import HTTPNotImplemented

from xbus.monitor.models.data_clearing import get_session
from xbus.monitor.models.data_clearing import Item

from .util import get_list
from .util import get_record
from . import view_decorators


_MODEL = 'cl_item'


@view_decorators.list(_MODEL)
def cl_item_list(request):

    # TODO Remove the custom record wrapper when clients represent
    # relationships better (for now, we just include the data they are going
    # to need in the result list).

    def record_wrapper(record):
        """Include type names."""
        ret = record.as_dict()
        ret['type_name'] = record.type.display_name
        return ret

    return get_list(
        Item, request.GET, sqla_session=get_session(request),
        record_wrapper=record_wrapper,
    )


@view_decorators.create(_MODEL)
def cl_item_create(request):
    raise HTTPNotImplemented(json_body={})


@view_decorators.read(_MODEL)
def cl_item_read(request):

    # TODO Send an event to Xbus asking for information about the item.

    record = get_record(request, _MODEL)
    return record.as_dict()


@view_decorators.update(_MODEL)
def cl_item_update(request):
    raise HTTPNotImplemented(json_body={})


@view_decorators.delete(_MODEL)
def cl_item_delete(request):
    raise HTTPNotImplemented(json_body={})


@view_decorators.patch(_MODEL)
def cl_item_patch(request):

    # TODO Send an event to Xbus asking to patch the item.

    record = get_record(request, _MODEL)
    return record.as_dict()
