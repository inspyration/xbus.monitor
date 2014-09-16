xbus.monitor README
===================

Install with Docker and Fig
---------------------------

Clone xbus_monitor and xbus_broker in the same directory. Move the fig.yml file to this parent directory::

  $ hg clone ssh://hg@bitbucket.org/xcg/xbus_monitor
  $ hg clone ssh://hg@bitbucket.org/xcg/xbus_broker
  $ ln -s xbus_monitor/fig.yml .
  $ mkdir etc
  $ cp xbus-monitor/production.ini etc/

Create a virtualenv with fig installed::

  $ virtualenv --no-site-packages --python=python2.7 env-fig
  $ pip install --upgrade fig
  $ source env-fig/bin/activate

Follow the "Install from sources" instructions in the xbus_broker README.rst file in order to compile the broker executable.

Build the dockers using Fig::

  $ fig build

Create the xbus user and database::

  $ fig run -d postgresql
  $ docker run -i -t --link xbus_postgresql_run_1:db xcgd/postgresql /bin/bash
  $ echo "create user xbus with password 'xbus'; create database xbus with owner = xbus" | psql -h db -p 5432 -U postgres
  $ exit
  $ docker stop xbus_postgresql_run_1


Configure the monitor by editing your config file in `etc/production.ini` and finally initialize the database::

  $ fig run --rm monitor initialize_monitor_db /opt/xbus/monitor/development.ini

Start XBus::

  $ fig up


Install without Docker
----------------------

::

  $ cd <directory containing this file>
  $ $VENV/bin/python setup.py develop
  $ $VENV/bin/initialize_monitor_db development.ini
  $ $VENV/bin/pserve development.ini

