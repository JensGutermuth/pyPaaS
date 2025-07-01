#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import sys

from . import options, util


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
                    cmd = os.path.join(os.path.dirname(sys.executable), 'pypaas') + ' $SSH_ORIGINAL_COMMAND'
                    if options.main.get('shell', None):
                        cmd = '{} -l -c \'{}\''.format(options.main.get['shell'], cmd)
                    lines.append(
                        ('command="{cmd} $SSH_ORIGINAL_COMMAND",' +
                         'no-agent-forwarding,no-user-rc,no-X11-forwarding,' +
                         'no-port-forwarding {key} {name}').format(
                            cmd=cmd,
                            key=key,
                            name=name
                        )
                    )
        util.replace_file(os.path.join(ssh_dir, 'authorized_keys'),
                          '\n'.join(lines)+'\n')
