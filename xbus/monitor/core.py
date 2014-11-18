import os
from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .i18n import init_i18n
from .models.models import DBSession
from .models.models import BaseModel


def _add_api_routes(config, model):
    """Register routes for a model to be exposed through the API. The relevant
    views then have to be implemented by referencing these routes.
    """

    config.add_route(
        '{model}_list'.format(model=model),
        '/api/{model}'.format(model=model),
        request_method='GET',
    )
    config.add_route(
        '{model}_create'.format(model=model),
        '/api/{model}'.format(model=model),
        request_method='POST',
    )
    config.add_route(
        model,
        '/api/{model}/{{id}}'.format(model=model),
        factory='xbus.monitor.factory.{model}'.format(model=model),
    )
    config.add_route(
        '{model}_rel_list'.format(model=model),
        '/api/{model}/{{id}}/{{rel}}'.format(model=model),
        request_method='GET',
        factory='xbus.monitor.factory.{model}'.format(model=model),
    )
    config.add_route(
        '{model}_rel_create'.format(model=model),
        '/api/{model}/{{id}}/{{rel}}'.format(model=model),
        request_method='POST',
        factory='xbus.monitor.factory.{model}'.format(model=model),
    )
    config.add_route(
        '{model}_rel'.format(model=model),
        '/api/{model}/{{id}}/{{rel}}/{{rid}}'.format(model=model),
        factory='xbus.monitor.factory.{model}'.format(model=model),
    )


def main(global_config, **settings):
    """Initiate a Pyramid WSGI application.
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

    config = Configurator(settings=settings)

    init_i18n(config)

    config.include('pyramid_chameleon')

    config.add_static_view('static', 'static', cache_max_age=3600)

    # Pages.

    config.add_route('home', '/')
    config.add_route('xml_config_ui', '/xml_config')
    config.add_route(
        'event_type_graph', '/api/event_type/{id}/graph',
        factory='xbus.monitor.factory.event_type'
    )

    # REST API exposed with JSON.

    _add_api_routes(config, 'emitter')
    _add_api_routes(config, 'emitter_profile')
    _add_api_routes(config, 'envelope')
    _add_api_routes(config, 'event')
    _add_api_routes(config, 'event_error')
    _add_api_routes(config, 'event_node')
    _add_api_routes(config, 'event_type')
    _add_api_routes(config, 'input_descriptor')
    _add_api_routes(config, 'role')
    _add_api_routes(config, 'service')

    config.add_route('xml_config', '/api/xml_config')

    config.scan()
    return config.make_wsgi_app()
