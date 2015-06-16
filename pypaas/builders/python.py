#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import subprocess

from .base import BaseBuilder


class PythonVirtualenvBuilder(BaseBuilder):
    def build(self):
        subprocess.check_call(
            ['virtualenv', 'venv'],
            cwd=self.checkout.path,
            env=self.checkout.cmd_env
        )


class PipBuilder(PythonVirtualenvBuilder):
    @property
    def is_applicable(self):
        return os.path.isfile(os.path.join(
            self.checkout.path, 'requirements.txt'
        ))

    def build(self):
        super(PipBuilder, self).build()
        subprocess.check_call(
            ['venv/bin/pip', 'install', '-r', 'requirements.txt'],
            cwd=self.checkout.path,
            env=self.checkout.cmd_env
        )


class SetupPyBuilder(PythonVirtualenvBuilder):
    @property
    def is_applicable(self):
        return os.path.isfile(os.path.join(self.checkout.path, 'setup.py'))

    def build(self):
        super(SetupPyBuilder, self).build()
        subprocess.check_call(
            ['venv/bin/pip', 'install', '-e', '.'],
            cwd=self.checkout.path,
            env=self.checkout.cmd_env
        )
