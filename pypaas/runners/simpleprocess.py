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

    try:
        os.unlink(os.path.expanduser('~/services/{}'.format(service)))
    except FileNotFoundError:
        pass

    try:
        os.unlink(os.path.expanduser('~/services-real/{}/run'.format(service)))
    except FileNotFoundError:
        pass
    try:
        os.unlink(os.path.expanduser('~/services-real/{}/log/run'.format(service)))
    except FileNotFoundError:
        pass

    subprocess.check_call([
        'svc', '-dx',
        os.path.expanduser('~/services-real/{}/log'.format(service))
    ])
    subprocess.check_call([
        'svc', '-dx',
        os.path.expanduser('~/services-real/{}'.format(service))
    ])
    shutil.rmtree(os.path.expanduser('~/services-real/{}'.format(service)))


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
        util.mkdir_p(os.path.expanduser('~/services-real/'))

        for idx, s in enumerate(self.service_names):
            util.mkdir_p(os.path.expanduser('~/services-real/{}/log'.format(s)))
            env = copy.deepcopy(self.branch.config['env'])
            self.call_hook('env', env=env, idx=idx)
            args = dict(
                checkout=self.branch.current_checkout,
                cmd=self.config['cmd'],
                env_cmds='\n'.join('export {}="{}"'.format(k, v) for k, v
                                   in env.items())
            )
            util.replace_file(
                os.path.expanduser('~/services-real/{}/log/run'.format(s)),
                logscript.format(**args),
                chmod=0o755
            )
            util.replace_file(
                os.path.expanduser('~/services-real/{}/run'.format(s)),
                runscript.format(**args),
                chmod=0o755
            )
            try:
                os.symlink(
                    os.path.expanduser('~/services-real/{}'.format(s)),
                    os.path.expanduser('~/services/{}'.format(s))
                )
            except FileExistsError:
                pass
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
        super().enable_maintenance()
        for s in self.service_names:
            svc_stop(s)

    def disable_maintenance(self):
        super().disable_maintenance()
        self.configure()

    @classmethod
    def cleanup(cls):
        # avoid circle
        from ..repo import Repo

        runner_configs = set()
        for r in Repo.all():
            for b in r.branches.values():
                for runner in b.runners.values():
                    if isinstance(runner, cls):
                        runner_configs.update(runner.service_names)

        processes_to_delete = []
        for f in os.listdir(os.path.expanduser('~/services-real')):
            if f not in runner_configs:
                processes_to_delete.append(f)
        for p in processes_to_delete:
            svc_destroy(p)
