from xbus.monitor.models.data_clearing import get_session
from xbus.monitor.models.data_clearing import EventType
from xbus.monitor.models.data_clearing import Item
from xbus.monitor.models.data_clearing import ItemColumn
from xbus.monitor.models.data_clearing import ItemJoin
from xbus.monitor.models.data_clearing import ItemType
from xbus.monitor.resources.records import GenericRecordFactory


class _BaseRecordFactory(GenericRecordFactory):
    """Base class for record factories in this module."""

    @property
    def sqla_session(self, request):
        return get_session(request)


class RecordFactory_cl_event_type(_BaseRecordFactory):
    sqla_model = EventType


class RecordFactory_cl_item(_BaseRecordFactory):
    sqla_model = Item


class RecordFactory_cl_item_column(_BaseRecordFactory):
    sqla_model = ItemColumn


class RecordFactory_cl_item_join(_BaseRecordFactory):
    sqla_model = ItemJoin


class RecordFactory_cl_item_type(_BaseRecordFactory):
    sqla_model = ItemType
