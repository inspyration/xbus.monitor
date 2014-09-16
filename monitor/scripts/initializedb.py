import os
import sys
import argparse

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
)

from ..models.models import (
    DBSession,
    Base,
)


def main(argv=sys.argv):

    parser = argparse.ArgumentParser()
    parser.add_argument('config_uri')
    parser.add_argument('-c', '--clear', action='store_true')
    parser.add_argument(
        '-d', '--demo', action='store', nargs='?', const='../demo'
    )
    args = parser.parse_args()
    config_uri = args.config_uri
    setup_logging(config_uri)

    settings = get_appsettings(config_uri)
    db_url = settings.get('fig.sqlalchemy.url')
    if db_url:
        pg_socket_var = os.getenv('XBUS_POSTGRESQL_1_PORT')
        if pg_socket_var is not None:
            pg_socket = pg_socket_var.split('://', 1)[-1]
        else:
            pg_socket = settings.get('fig.sqlalchemy.default.socket')
        settings['sqlalchemy.url'] = db_url.format(socket=pg_socket)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

    here = os.path.abspath(os.path.dirname(__file__))
    if args.clear:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with open(os.path.join(here, 'func.sql')) as f:
        engine.execute(f.read())
    if args.demo:
        copy_sql = "copy {table} ({cols}) from stdin csv;"
        seq_sql = "SELECT setval('{table}_id_seq'," \
                  "(SELECT MAX(id) FROM {table}))"
        demo_dir = os.path.join(here, args.demo)
        print [t.name for t in Base.metadata.sorted_tables]
        for t in Base.metadata.sorted_tables:
            print t.name
            table = t.name
            fpath = os.path.join(demo_dir, "{table}.csv".format(table=table))
            if os.path.isfile(fpath):
                with open(fpath) as stdin:
                    cols = stdin.readline()[:-1]
                    sql = copy_sql.format(table=table, cols=cols)
                    engine.execute("BEGIN")
                    engine.raw_connection().cursor().copy_expert(sql, stdin)
                    engine.execute("COMMIT")
                    if hasattr(t.c, 'id'):
                        engine.execute(seq_sql.format(table=table))
#    with transaction.manager:
#        model = MyModel(name='one', value=1)
#        DBSession.add(model)
