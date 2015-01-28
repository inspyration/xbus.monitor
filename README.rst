xbus.monitor
============

This package provides tools to monitor and administer Xbus.

TODO Link to Xbus.

Note: this package provides a REST API but no GUI; separate packages implement
it.

Current packages providing an interface to xbus.monitor:

- xbus_monitor_js <https://bitbucket.org/xcg/xbus_monitor_js>: Single-page
  JavaScript Backbone application that communicates with xbus.monitor via its
  REST API.


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

Set up a virtualenv::
    $ mkvirtualenv xbus

Clone xbus.broker and install it::
    $ hg clone ssh://hg@bitbucket.org/xcg/xbus.broker
    $ pip install xbus.broker

Clone this project and install it::
    $ hg clone https://bitbucket.org/xcg/xbus.monitor
    $ pip install xbus.monitor

Install and setup xbus.broker (follow its README file for instructions).

Create a configuration file based on production.ini.sample and edit it.

Run the monitor::

  $ $VENV/bin/pserve path-to-config-file


Configuration details
---------------------

Only use en_US or fr_FR for now in pyramid.default_locale_name

Localization:

    Edit the "pyramid.default_locale_name" variable.


Run
---

With Docker::

    fig up

Without Docker::

    $VENV/bin/pserve path-to-config-file


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
