#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import subprocess

from .base import BaseBuilder


class NPMBuilder(BaseBuilder):
    @property
    def is_applicable(self):
        return os.path.isfile(os.path.join(self.checkout.path, 'package.json'))

    def build(self):
        subprocess.check_call(
            ['npm', 'install'],
            cwd=self.checkout.path
        )


class BowerBuilder(BaseBuilder):
    @property
    def is_applicable(self):
        return os.path.isfile(os.path.join(self.checkout.path, 'bower.json'))

    def build(self):
        subprocess.check_call(
            ['bower', 'install'],
            cwd=self.checkout.path
        )
