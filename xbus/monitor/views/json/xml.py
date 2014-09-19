from pyramid.view import view_config
from pyramid.response import Response

from ...utils.xml_config import load_config


@view_config(route_name='xml_config', request_method='GET')
def config_get(request):
    return Response(status_int=501, content_type="application/json")


@view_config(route_name='xml_config', request_method='POST')
def config_post(request):
    xml = request.json_body['xml']
    load_config(xml)
    return Response(status_int=204, content_type="application/json")
