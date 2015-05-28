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
    subprocess.check_call([
        'svc', '-u',
        os.path.expanduser('~/services/{}'.format(service))
    ])


def svc_stop(service):
    subprocess.check_call([
        'svc', '-d',
        os.path.expanduser('~/services/{}'.format(service))
    ])


def svc_destroy(service):
    subprocess.check_call([
        'svc', '-x',
        os.path.expanduser('~/services/{}'.format(service))
    ])
    subprocess.check_call([
        'svc', '-x',
        os.path.expanduser('~/services/{}/log'.format(service))
    ])


class SimpleProcess(BaseRunner, util.HooksMixin):
    config_key = 'run_simpleprocess'

    @property
    def name(self):
        return '-'.join([
            self.__class__.__name__,
            self.app.repo.name,
            self.app.name
        ])

    @property
    def is_applicable(self):
        return self.config_key in self.app.config

    @property
    def config(self):
        return self.app.config[self.config_key]

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
            env = copy.deepcopy(self.app.config['env'])
            self.call_hook('env', env=env, idx=idx)
            args = dict(
                checkout=self.app.current_checkout,
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

    def start(self):
        for s in self.service_names:
            svc_start(s)

    def stop(self):
        for s in self.service_names:
            svc_stop(s)

    def destroy(self):
        for s in self.service_names:
            path = os.path.expanduser('~/services/{}'.format(s))
            if os.path.isdir(path):
                svc_destroy(s)
                shutil.rmtree(path)
