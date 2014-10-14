FROM ubuntu:14.04
MAINTAINER jeremie.gavrel@xcg-consulting.fr 

RUN apt-get update && apt-get -yq install python-dev python-pip python-pyramid python-pyramid-tm python-psycopg2 python-sqlalchemy python-transaction python-waitress python-zope.sqlalchemy libzmq3-dev 

RUN pip install pyramid pyramid_chameleon pyramid_debugtoolbar pyramid_tm psycopg2 SQLAlchemy transaction waitress zope.sqlalchemy msgpack-python pyzmq

ADD . /opt/xbus/monitor

RUN cd /opt/xbus/monitor && python /opt/xbus/monitor/setup.py install

EXPOSE 6543 

CMD ["pserve","/opt/xbus/monitor/etc/production.ini"]
