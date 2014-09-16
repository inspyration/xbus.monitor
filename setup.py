import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'pyramid',
    'pyramid_chameleon',
    'pyramid_debugtoolbar',
    'pyramid_tm',
    'psycopg2',
    'SQLAlchemy',
    'transaction',
    'waitress',
    'zope.sqlalchemy',
]

setup(name='xbus.monitor',
      version='0.0',
      description='XBus Monitor',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='',
      author_email='',
      url='',
      keywords='xbus web pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='xbus.monitor',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = xbus.monitor:main
      [console_scripts]
      initialize_monitor_db = xbus.monitor.scripts.initializedb:main
      """,
      )
