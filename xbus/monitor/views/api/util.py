from ...models.models import DBSession


def get_list(sqla_model, params=None, query=None):
    """Helper to retrieve a record list, encoded with JSON."""
    if query is None:
        query = DBSession.query(sqla_model)
    if params is None:
        params = {}
    for param_op, value in params.iteritems():

        if len(param_op) >= 3 and param_op[-3] == ':':
            param, op = param_op[:-3], param_op[-2:]
        elif value:
            param, op = param_op, 'eq'
        else:
            param, op = param_op, 'is'

        if hasattr(sqla_model, 'c'):
            col = sqla_model.c.get(param, None)
        else:
            col = getattr(sqla_model, param, None)
        if col is None:
            continue

        if op == 'is':
            if value.lower() == 'true':
                query = query.filter(col != None)
            else:
                query = query.filter(col == None)
        elif op == 'eq':
            query = query.filter(col == value)
        elif op == 'ne':
            query = query.filter(col != value)
        elif op == 'gt':
            query = query.filter(col > (value if value else None))
        elif op == 'ge':
            query = query.filter(col >= (value if value else None))
        elif op == 'lt':
            query = query.filter(col < (value if value else None))
        elif op == 'le':
            query = query.filter(col <= (value if value else None))

    records = query.all()
    return [record.as_dict() for record in records]
