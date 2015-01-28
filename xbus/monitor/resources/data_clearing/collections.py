from pyramid import security

from xbus.monitor.models.data_clearing import EventType
from xbus.monitor.models.data_clearing import Item
from xbus.monitor.models.data_clearing import ItemColumn
from xbus.monitor.models.data_clearing import ItemJoin
from xbus.monitor.models.data_clearing import ItemType
from xbus.monitor.resources.root import RootFactory


class _GenericCollectionFactory(RootFactory):
    """Factory for collections of records; provides:
    - sqla_model: sqlalchemy class.
    """

    sqla_model = None  # To be overridden by derived classes.

    # Give any authenticated user full access to all models by default, unless
    # the ACL is specialized in the derived class.
    # TODO Wrong but easier for tests...
    __acl__ = [
        (security.Allow, security.Authenticated, 'create'),
        (security.Allow, security.Authenticated, 'read'),
        (security.Allow, security.Authenticated, 'update'),
        (security.Allow, security.Authenticated, 'delete'),
    ]


class CollectionFactory_cl_event_type(_GenericCollectionFactory):
    sqla_model = EventType


class CollectionFactory_cl_item(_GenericCollectionFactory):
    sqla_model = Item


class CollectionFactory_cl_item_column(_GenericCollectionFactory):
    sqla_model = ItemColumn


class CollectionFactory_cl_item_join(_GenericCollectionFactory):
    sqla_model = ItemJoin


class CollectionFactory_cl_item_type(_GenericCollectionFactory):
    sqla_model = ItemType
