#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import subprocess

from .base import BaseBuilder


class NPMBuilder(BaseBuilder):
    @property
    def is_applicable(self):
        return os.path.isfile(os.path.join(self.checkout.path, 'package.json'))

    def delete_npm_crap(self):
        """
        Delete all the crap npm likes to leave behind in /tmp/npm-*
        """
        for name in os.listdir('/tmp'):
            fullname = os.path.join('/tmp', name)
            if not name.startswith('npm-') or not os.path.isdir(fullname):
                continue
            try:
                shutil.rmtree(fullname)
            except:
                pass

    def build(self):
        self.delete_npm_crap()

        subprocess.check_call(
            ['npm', 'install'],
            cwd=self.checkout.path,
            env=self.checkout.cmd_env
        )

        self.delete_npm_crap()


class BowerBuilder(BaseBuilder):
    @property
    def is_applicable(self):
        return os.path.isfile(os.path.join(self.checkout.path, 'bower.json'))

    def build(self):
        subprocess.check_call(
            ['bower', 'install'],
            cwd=self.checkout.path,
            env=self.checkout.cmd_env
        )
