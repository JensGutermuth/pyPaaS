"""Configuration storage and loading for PyPaaS."""
import errno
import os
import os.path

import yaml

from configparser import ConfigParser

main = {}
repos = {}


def load_config():
    """Load configuration from disk."""
    global main
    global apps
    for configpath in ['~/config', '/etc/pypaas']:
        configpath = os.path.expanduser(configpath)
        if os.path.isfile(os.path.join(configpath, 'pypaas.yml')):
            main = yaml.load(open(os.path.join(configpath, 'pypaas.yml')))
            for repo in os.listdir(os.path.join(configpath, 'repos')):
                if not repo.endswith('.yml'):
                    continue
                repo = repo[:-(len('.yml'))]
                repos[repo] = yaml.load(open(
                    os.path.join(configpath, 'repos', repo + '.yml')
                ))
            break

load_config()

BASEPATH = os.path.expanduser('~')
