from xml.etree import ElementTree

from ..models.models import DBSession
from ..models.models import Role
from ..models.models import Service
from ..models.models import Emitter
from ..models.models import EventType
from ..models.models import EventNodeRel
from ..models.models import EmitterProfile
from ..models.models import EmitterProfileEventTypeRel
from ..models.models import EventNode


def load_config(raw_xml):
    root = ElementTree.fromstring(raw_xml)
    session = DBSession()
    services = {}
    events = {}

    for service_elem in root.findall('service'):
        name = service_elem.get('name')
        consumer = service_elem.get('consumer', False)
        description = service_elem.text
        q = session.query(Service).filter(Service.name == name)
        service = q.first()
        if not service:
            service = Service(name=name, consumer=consumer, description=description)
        services[name] = service
        session.add(service)

    for role_elem in root.findall('role'):
        login = role_elem.get('login')
        if not login:
            login = role_elem.get('name')
        service_name = role_elem.get('service')
        service = services.get(service_name)
        if not service:
            q1 = session.query(Service)
            q1 = q1.filter(Service.name == service_name)
            service = q1.first()
        q2 = session.query(Role)
        q2 = q2.filter(Role.login == login)
        r = q2.first()
        if not r:
            r = Role(login=login, service=service)
        session.add(r)

    for event_elem in root.findall('event_type'):
        name = event_elem.get('name')
        description = event_elem.text
        q = session.query(Service)
        q = q.filter(Service.name == name)
        e = q.first()
        if not e:
            e = EventType(name=name, description=description)
        events[name] = e
        session.add(e)
