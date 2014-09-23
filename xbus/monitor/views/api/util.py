from xbus.monitor.models.models import DBSession


def get_list(name, sqla_model):
    """Helper to retrieve a record list, encoded with JSON."""
    query = DBSession.query(sqla_model)
    records = query.all()
    return {name: [record.as_dict() for record in records]}
