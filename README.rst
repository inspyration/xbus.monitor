xbus.monitor README
===================

Install with Docker and Fig
---------------------------

Clone xbus_monitor and xbus_broker in the same directory. Move the fig.yml file to this parent directory::

  $ hg clone ssh://hg@bitbucket.org/xcg/xbus_monitor
  $ hg clone ssh://hg@bitbucket.org/xcg/xbus_broker
  $ mv xbus_monitor/fig.yml .

Follow the "Install from sources" instructions in the xbus_broker README.rst file in order to compile the broker executable.

Build the dockers using Fig::

  $ fig build

Create the xbus user and database::

  $ fig start postgresql
  $ echo "create user xbus with password 'xbus'; create database xbus with owner = xbus | psql -h 127.0.0.1 -p 54321 -U postgres
  $ fig stop postgresql

Initialize the database (option -d to load the demo data, -c to clear existing tables)::

  $ fig run monitor initialize_monitor_db /opt/xbus/monitor/development.ini

Start XBus::

  $ fig up


Install without Docker
----------------------

::

  $ cd <directory containing this file>
  $ $VENV/bin/python setup.py develop
  $ $VENV/bin/initialize_monitor_db development.ini
  $ $VENV/bin/pserve development.ini

