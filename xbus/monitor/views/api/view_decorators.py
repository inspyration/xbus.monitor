"""Helpers around Pyramid "view_config" decorators for the REST API.
"""

from pyramid.view import view_config


def _merge_settings(settings, default_settings):
    default_settings.update({
        'http_cache': 0,
        'renderer': 'json',
    })
    default_settings.update(settings)
    return default_settings


class list(view_config):
    def __init__(self, model, **settings):
        super(list, self).__init__(**_merge_settings(settings, {
            'route_name': '%s_list' % model,
        }))


class create(view_config):
    def __init__(self, model, **settings):
        super(create, self).__init__(**_merge_settings(settings, {
            'permission': 'create',
            'route_name': '%s_create' % model,
        }))


class read(view_config):
    def __init__(self, model, **settings):
        super(read, self).__init__(**_merge_settings(settings, {
            'permission': 'read',
            'request_method': 'GET',
            'route_name': model,
        }))


class update(view_config):
    def __init__(self, model, **settings):
        super(update, self).__init__(**_merge_settings(settings, {
            'permission': 'update',
            'request_method': 'PUT',
            'route_name': model,
        }))


class delete(view_config):
    def __init__(self, model, **settings):
        super(delete, self).__init__(**_merge_settings(settings, {
            'permission': 'delete',
            'request_method': 'DELETE',
            'route_name': model,
        }))
