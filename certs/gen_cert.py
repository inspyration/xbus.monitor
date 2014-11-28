import argparse
import os
import sys

sys.path.append('./data')

parser = argparse.ArgumentParser(
    description='Generate files for Authentic connection.'
)
parser.add_argument(
    '-p',
    '--pyramid',
    help='host:port',
    default='localhost:6543'
)
parser.add_argument(
    '-a',
    '--authentic',
    help='host:port',
    default='localhost:8000'
)
args = parser.parse_args()

pyramid_host = args.pyramid.split(':')
authentic_host = args.authentic.split(':')

os.system('sh data/gen_cert.sh %s %s %s %s' % (
    authentic_host[0], authentic_host[1],
    pyramid_host[0], pyramid_host[1],
))
