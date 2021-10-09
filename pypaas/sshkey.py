#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import sys

from . import util


class SSHKey(object):
    @staticmethod
    def rebuild_authorized_keys():
        lines = []
        ssh_dir = os.path.expanduser('~/.ssh')
        util.mkdir_p(os.path.join(ssh_dir, 'authorized_keys.d'))

        for name in os.listdir(os.path.join(ssh_dir, 'authorized_keys.d')):
            keyfilename = os.path.join(ssh_dir, 'authorized_keys.d', name)
            with open(keyfilename) as keyfile:
                for key in keyfile:
                    keyparts = key.split()
                    assert keyparts[0].startswith('ssh-') or keyparts[0].startswith('ecdsa-')
                    key = ' '.join(keyparts[:2])
                    name = name.replace('.pub', '')
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
                          '\n'.join(lines)+'\n')
