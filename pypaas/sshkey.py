#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import sys

from . import util


class SSHKey(object):
    def __init__(self, name):
        self.name = name

    @classmethod
    def create(cls, name, key):
        self = cls(name)
        self.save_key(key)

    @classmethod
    def rebuild_authorized_keys(cls):
        lines = []
        ssh_dir = os.path.expanduser('~/.ssh')
        util.mkdir_p(os.path.join(ssh_dir, 'authorized_keys.d'))
        print()
        for name in os.listdir(os.path.join(ssh_dir, 'authorized_keys.d')):
            key = open(os.path.join(ssh_dir, 'authorized_keys.d', name)).read()
            lines.append(
                ('command="{pypaas_cmd} $SSH_ORIGINAL_COMMAND",' +
                 'no-agent-forwarding,no-user-rc,no-X11-forwarding,' +
                 'no-port-forwarding {key} {name}').format(
                    pypaas_cmd=os.path.join(
                        os.path.dirname(sys.executable), 'pypaas'
                    ),
                    key=key,
                    name=name
                )
            )
        util.replace_file(os.path.join(ssh_dir, 'authorized_keys'),
                          '\n'.join(lines))

    def save_key(self, key):
        keyparts = key.split()
        assert keyparts[0].startswith('ssh-')
        key = ' '.join(keyparts[:2])

        ssh_dir = os.path.expanduser('~/.ssh')
        util.mkdir_p(os.path.join(ssh_dir, 'authorized_keys.d'))
        keyfilepath = os.path.join(ssh_dir, 'authorized_keys.d', self.name)
        with open(keyfilepath, 'w') as keyfile:
            keyfile.write(key)

        self.rebuild_authorized_keys()
