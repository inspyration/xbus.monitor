xbus.monitor README
===================

This module is new generation of open source tool for Enterprise
Application Integration (EAI).
Xbus offers services with high added value and for interpreting and
transforming activities by events.
The solution consists of a flexible middleware that connects all internal
and external systems.
An instance manages the interactions between controlled and optimized all systems.

You can also find a presentation at http://bit.ly/1AYtQa6


Install with Docker and Fig
---------------------------

Clone xbus_monitor and xbus_broker in the same directory. Move the fig.yml file to this parent directory::

  $ hg clone ssh://hg@bitbucket.org/xcg/xbus_monitor
  $ hg clone ssh://hg@bitbucket.org/xcg/xbus.broker
  $ ln -s xbus_monitor/fig.yml .
  $ mkdir etc
  $ cp xbus_monitor/production.ini.sample etc/production.ini

Create a virtualenv with fig installed::

  $ virtualenv --no-site-packages --python=python2.7 env-fig
  $ pip install --upgrade fig
  $ source env-fig/bin/activate

Follow the "Install from sources" instructions in the xbus_broker README.rst file in order to compile the broker executable.

Build the dockers using Fig::

  $ fig build

Create the xbus user and database::

  $ docker run -d --name="xbus_postgresql_1" xcgd/postgresql
  $ docker run --rm -i -t --link xbus_postgresql_1:db xcgd/postgresql /bin/bash
  $ echo "create user xbus with password 'xbus'; create database xbus with owner = xbus" | psql -h db -p 5432 -U postgres
  $ echo 'CREATE EXTENSION IF NOT EXISTS "uuid-ossp"' | psql -h db -p 5432 -U postgres
  $ exit
  $ docker stop xbus_postgresql_1


Initialize the database::

  $ fig run --rm monitor setup_xbusbroker

[Deprecated]::
  $ fig run --rm monitor initialize_monitor_db /opt/xbus/monitor/etc/production.ini

Start Xbus::

  $ fig up


Install without Docker
----------------------

::

  $ cd <directory containing this file>
  $ $VENV/bin/python setup.py develop
  $ $VENV/bin/setup_xbusbroker

[Deprecated]::
  $ $VENV/bin/initialize_monitor_db development.ini


Configure
---------

Copy production-sample.ini to development.ini and edit it.

Only use en_US or fr_FR for now in pyramid.default_locale_name

Localization:

    Edit the "pyramid.default_locale_name" variable.


Run
---

With Docker::

    fig up

Without Docker::

    $VENV/bin/pserve development.ini


Run tests
---------
::

    nosetests


Generate the translation template
---------------------------------
::

    pip install Babel lingua
    python setup.py extract_messages


Other translation tasks
-----------------------
See <http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/i18n.html>.
::

    python setup.py [init_catalog -l en_US] [update_catalog] [compile_catalog]


Thanks
------

xbus.monitor uses the following external projects; thanks a lot to their respective authors:
- pyramid <http://docs.pylonsproject.org/projects/pyramid/en/latest/>
- pyramid_httpauth <https://github.com/tarzanjw/pyramid_httpauth>
