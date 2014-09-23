import os
from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models.models import DBSession
from .models.models import Base


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
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
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)

    # Pages.

    config.add_route('home', '/')
    config.add_route('xml_config_ui', '/xml_config')

    # REST API exposed with JSON.

    config.add_route(
        'event_type_list',
        '/api/event_type',
        request_method='GET',
    )
    config.add_route(
        'event_type_create',
        '/api/event_type',
        request_method='POST',
    )
    config.add_route(
        'event_type',
        '/api/event_type/{id}',
        factory='xbus.monitor.factory.event_type',
    )

    config.add_route('xml_config', '/api/xml_config')

    config.scan()
    return config.make_wsgi_app()
