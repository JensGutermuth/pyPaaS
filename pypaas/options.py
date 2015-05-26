
import errno
import os

from configparser import ConfigParser

global_config = ConfigParser()
global_config.read_string('''
[pyPaaS]
base_directory=/tmp/pyPaaS
''')
global_config.read('/etc/pyPaaS.ini')
global_config.read('~/pyPaaS.ini')

BASEPATH = global_config.get('pyPaaS', 'base_directory')
