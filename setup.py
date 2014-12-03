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
    'pyramid_httpauth',
    'pyramid_redis_sessions==1.0a1',
    'pyramid_tm',
    'psycopg2',
    'redis==2.9.1',
    'six',
    'SQLAlchemy',
    'transaction',
    'waitress',
    'zope.sqlalchemy',
    'pyzmq',
    'msgpack-python',
]

setup(
    name='xbus.monitor',
    version='0.0',
    description='Xbus Monitor',
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
    tests_require=requires,
    entry_points="""\
    [paste.app_factory]
    main = xbus.monitor:main
    """,
    message_extractors={'xbus.monitor': [
        ('xbus/monitor/**.py', 'lingua_python', None),
        ('xbus/monitor/templates/**.pt', 'lingua_xml', None),
    ]},
)
