FROM ubuntu:14.04
MAINTAINER jeremie.gavrel@xcg-consulting.fr 

RUN apt-get update && apt-get -yq install python-dev python-pip python-pyramid python-pyramid-tm python-psycopg2 python-sqlalchemy python-transaction python-waitress python-zope.sqlalchemy

ADD . /opt/xbus/monitor

RUN cd /opt/xbus/monitor && python /opt/xbus/monitor/setup.py install

EXPOSE 6543 

CMD ["pserve","/opt/xbus/monitor/etc/development.ini"]
