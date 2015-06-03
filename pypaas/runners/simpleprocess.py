#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import os
import os.path
import shutil
import subprocess
import sys
import time

from .. import util
from .base import BaseRunner


runscript = """#!/bin/sh
cd {checkout.path}
{env_cmds}
exec 2>&1
exec {cmd}
"""

logscript = """#!/bin/sh
exec multilog t ./main
"""


def svc_start(service):
    print('starting daemontools service {}'.format(service))
    subprocess.check_call([
        'svc', '-u',
        os.path.expanduser('~/services/{}'.format(service))
    ])


def svc_stop(service):
    print('stopping daemontools service {}'.format(service))
    subprocess.check_call([
        'svc', '-d',
        os.path.expanduser('~/services/{}'.format(service))
    ])


def svc_destroy(service):
    print('destorying daemontools service {}'.format(service))
    svc_stop(service)
    svc_stop(service + '/log')

    try:
        os.unlink(os.path.expanduser('~/services/{}/run'.format(service)))
    except FileNotFoundError:
        pass
    try:
        os.unlink(os.path.expanduser('~/services/{}/log/run'.format(service)))
    except FileNotFoundError:
        pass

    subprocess.check_call([
        'svc', '-x',
        os.path.expanduser('~/services/{}'.format(service))
    ])
    subprocess.check_call([
        'svc', '-x',
        os.path.expanduser('~/services/{}/log'.format(service))
    ])


def svc_wait(service):
    print('waiting for daemontools service {} to appear'.format(service))
    out = None
    while (out is None) or (b"supervise not running" in out) or \
            (b"unable to control" in out):
        out = subprocess.check_output([
            'svstat',
            os.path.expanduser('~/services/{}'.format(service))
        ])
        time.sleep(0.05)


class SimpleProcess(BaseRunner, util.HooksMixin):
    @property
    def service_names(self):
        return ['{}-{}'.format(self.name, i)
                for i in range(self.config.get('process_count', 1))]

    def configure(self):
        util.mkdir_p(os.path.expanduser('~/services/'))
        for s in os.listdir(os.path.expanduser('~/services')):
            # clean up any old service definitions
            if s.startswith(self.name + '-') and s not in self.service_names:
                svc_destroy(s)
                shutil.rmtree(os.path.join(
                    os.path.expanduser('~/services'), s
                ))

        for idx, s in enumerate(self.service_names):
            util.mkdir_p(os.path.expanduser('~/services/{}/log'.format(s)))
            env = copy.deepcopy(self.branch.config['env'])
            self.call_hook('env', env=env, idx=idx)
            args = dict(
                checkout=self.branch.current_checkout,
                cmd=self.config['cmd'],
                env_cmds='\n'.join('export {}="{}"'.format(k, v) for k, v
                                   in env.items())
            )
            util.replace_file(
                os.path.expanduser('~/services/{}/log/run'.format(s)),
                logscript.format(**args),
                chmod=0o755
            )
            util.replace_file(
                os.path.expanduser('~/services/{}/run'.format(s)),
                runscript.format(**args),
                chmod=0o755
            )
        for s in self.service_names:
            svc_wait(s)
            svc_start(s)

    def deconfigure(self):
        for s in self.service_names:
            path = os.path.expanduser('~/services/{}'.format(s))
            if os.path.isdir(path):
                svc_destroy(s)
                shutil.rmtree(path)

    def enable_maintenance(self):
        for s in self.service_names:
            svc_stop(s)

    def disable_maintenance(self):
        self.configure()
