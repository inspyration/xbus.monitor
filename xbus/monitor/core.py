import os
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from xbus.monitor import http_auth
from xbus.monitor.i18n import init_i18n
from xbus.monitor.models.models import DBSession
from xbus.monitor.resources.root import RootFactory


# Where the REST API is located.
API_PREFIX = '/api/'


# Where to find factories for individual records.
RECORD_FACTORY_LOC = 'xbus.monitor.resources.records.RecordFactory_{model}'


def _add_api_routes(config, model):
    """Register routes for a model to be exposed through the API. The relevant
    views then have to be implemented by referencing these routes.
    """

    config.add_route(
        '{model}_list'.format(model=model),
        '{api_prefix}{model}'.format(
            api_prefix=API_PREFIX, model=model,
        ),
        request_method='GET',
    )
    config.add_route(
        '{model}_create'.format(model=model),
        '{api_prefix}{model}'.format(
            api_prefix=API_PREFIX, model=model,
        ),
        request_method='POST',
    )
    config.add_route(
        model,
        '{api_prefix}{model}/{{id}}'.format(api_prefix=API_PREFIX, model=model),
        factory=RECORD_FACTORY_LOC.format(model=model),
    )
    config.add_route(
        '{model}_rel_list'.format(model=model),
        '{api_prefix}{model}/{{id}}/{{rel}}'.format(
            api_prefix=API_PREFIX, model=model,
        ),
        request_method='GET',
        factory=RECORD_FACTORY_LOC.format(model=model),
    )
    config.add_route(
        '{model}_rel_create'.format(model=model),
        '{api_prefix}{model}/{{id}}/{{rel}}'.format(
            api_prefix=API_PREFIX, model=model,
        ),
        request_method='POST',
        factory=RECORD_FACTORY_LOC.format(model=model),
    )
    config.add_route(
        '{model}_rel'.format(model=model),
        '{api_prefix}{model}/{{id}}/{{rel}}/{{rid}}'.format(
            api_prefix=API_PREFIX, model=model,
        ),
        factory=RECORD_FACTORY_LOC.format(model=model),
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

    http_auth.setup()

    config = Configurator(
        settings=settings,
        root_factory=RootFactory,
    )

    config.include('pyramid_chameleon')
    config.include('pyramid_httpauth')

    config.set_authorization_policy(ACLAuthorizationPolicy())

    # All views are protected by default; to provide an anonymous view, use
    # permission=pyramid.security.NO_PERSMISSION_REQUIRED.
    config.set_default_permission('view')

    init_i18n(config)

    config.add_static_view('static', 'static', cache_max_age=3600)

    # Pages.

    config.add_route('home', '/')
    config.add_route('xml_config_ui', '/xml_config')
    config.add_route(
        'event_type_graph', API_PREFIX + 'event_type/{id}/graph',
        factory=RECORD_FACTORY_LOC.format(model='event_type'),
    )

    # REST API exposed with JSON.

    _add_api_routes(config, 'emission_profile')
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

    # Other parts of the API.

    config.add_route('upload', API_PREFIX + 'upload')
    config.add_route('xml_config', API_PREFIX + 'xml_config')

    # Process view declarations.
    config.scan()

    # Run!
    return config.make_wsgi_app()
