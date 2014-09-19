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

    config.add_route('home', '/')

    config.add_route('xml_config', '/json/config/xml')
    config.add_route('event_config_list', '/json/config/event')
    config.add_route('event_config', '/json/config/event/{id}')

    # HTML event config interface
    config.add_route('html_xml_config', '/html/config')
    config.add_route('html_event_config_list', '/html/config/event')
    config.add_route('html_event_config_create', '/html/config/event/new')
    config.add_route('html_event_config_read', '/html/config/event/{id}')
    config.add_route('html_event_config_edit', '/html/config/event/{id}/edit')
    config.add_route(
        'html_event_config_delete', '/html/config/event/{id}/delete'
    )
    config.scan()
    return config.make_wsgi_app()
