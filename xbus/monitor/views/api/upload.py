import aiozmq
from aiozmq import rpc
import asyncio
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import view_config


@asyncio.coroutine
def _coro_emitter(front_url, login, password, items, loop):
    """The actual emission logic.

    @return The envelope ID and logs.
    @rtype (envelope-ID, log list) tuple.
    """

    item_count = len(items)

    logs = []

    logs.append('Establishing RPC connection...')
    client = yield from rpc.connect_rpc(connect=front_url, loop=loop)
    logs.append('RPC connection OK')
    token = yield from client.call.login(login, password)
    logs.append('Got connection token: %s' % token)

    envelope_id = yield from client.call.start_envelope(token)
    logs.append('Started envelope: %s' % envelope_id)

    event_id = yield from client.call.start_event(
        token, envelope_id, 'test_event', 0
    )
    logs.append('Started event: %s' % event_id)

    logs.append('Sending %d items...' % item_count)
    for item in items:
        yield from client.call.send_item(
            token, envelope_id, event_id, item
        )
    logs.append('Sent %d items' % item_count)

    yield from client.call.end_event(token, envelope_id, event_id)
    logs.append('Ended event: %s' % event_id)

    yield from client.call.end_envelope(token, envelope_id)
    logs.append('Ended envelope: %s' % envelope_id)

    yield from client.call.logout(token)
    logs.append('Logged out; terminating')

    client.close()
    logs.append('Done.')

    return envelope_id, logs


@view_config(
    route_name='upload',
    request_method='POST',
    renderer='json',
    http_cache=0,
)
def upload(request):
    """View to handle file uploads. They are sent to Xbus.
    """

    emission_profile_id = request.params.get('emission_profile_id')
    if not emission_profile_id:
        raise HTTPBadRequest(
            json_body={'error': 'No emission profile selected'},
        )

    # TODO Ensure execution of the emission profile is authorized for the
    # current user.

    # TODO Use the selected encoding when decoding the file.

    # Split the file by line.
    file = request.params.get('file')
    items = [
        item.encode('utf-8')
        for item in file.value.decode('utf-8').splitlines()
    ]

    # TODO config params
    # The login & password must exist in the "emitter" database table.
    front_url = 'tcp://127.0.0.1:1984'
    login = 'upload_emitter'
    password = 'test'

    # Send our data via 0mq to the Xbus front-end.
    zmq_loop = aiozmq.ZmqEventLoopPolicy().new_event_loop()
    emitter = _coro_emitter(front_url, login, password, items, zmq_loop)
    envelope_id, logs = zmq_loop.run_until_complete(emitter)

    return {'envelope_id': envelope_id, 'logs': logs}
