#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import shutil
import subprocess
import sys

from .. import util
from .base import BaseRunner


runscript = """#!/bin/sh
export PATH=$PATH:{checkout.path}
exec {cmd}
"""


class SimpleProcess(BaseRunner):
    @property
    def name(self):
        return '{}-{}-{}-{}'.format(
            self.__class__.__name__,
            self.checkout.app.name, self.checkout.name,
            self.checkout.commit[:11]
        )

    @property
    def is_applicable(self):
        return self.checkout.config.has_section('runner:simpleprocess')

    def create(self):
        util.mkdir_p(os.path.expanduser('~/services/{}'.format(self.name)))
        util.replace_file(
            os.path.expanduser('~/services/{}/run'.format(self.name)),
            runscript.format(
                checkout=self.checkout,
                cmd=self.checkout.config.get('runner:simpleprocess', 'cmd')
            ),
            chmod=0o755
        )
        self.start()

    def start(self):
        subprocess.check_call([
            'svc', '-u',
            os.path.expanduser('~/services/{}'.format(self.name))
        ])

    def stop(self):
        subprocess.check_call([
            'svc', '-d',
            os.path.expanduser('~/services/{}'.format(self.name))
        ])

    def destroy(self):
        path = os.path.expanduser('~/services/{}'.format(self.name))
        if os.path.isdir(path):
            self.stop()
            subprocess.check_call([
                'svc', '-x',
                path
            ])
            shutil.rmtree(path)
