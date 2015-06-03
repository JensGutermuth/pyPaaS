"""Configuration storage and loading for PyPaaS."""
import errno
import os
import os.path

import yaml

from configparser import ConfigParser

main = {}
repos = {}
domains = {}


def load_config():
    """Load configuration from disk."""
    global main
    global repos
    global domains
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
            for domain in os.listdir(os.path.join(configpath, 'domains')):
                if not domain.endswith('.yml'):
                    continue
                domain = domain[:-(len('.yml'))]
                domains[domain] = yaml.load(open(
                    os.path.join(configpath, 'domains', domain + '.yml')
                ))
            break

load_config()

BASEPATH = os.path.expanduser('~')
