#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import os
import os.path
import shutil
import subprocess

from configparser import ConfigParser

from . import builders, options


class Checkout(object):
    def __init__(self, app, commit, name):
        self.app, self.commit, self.name = app, commit, name

    @property
    def path(self):
        return os.path.join(
            options.BASEPATH, 'checkouts', self.app.repo.name, self.app.name,
            '{}-{}'.format(self.name, self.commit[:11])
        )

    @classmethod
    def create(cls, app, commit):
        name = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        self = cls(app, commit, name)
        subprocess.check_call(
            ['git', 'clone', '-q', self.app.repo.path, self.path],
            env={}
        )
        subprocess.check_call(
            ['git', 'config', 'advice.detachedHead', 'false'],
            env={}, cwd=self.path
        )
        subprocess.check_call(
            ['git', 'checkout', self.commit],
            env={}, cwd=self.path
        )
        subprocess.check_call(
            ['git', 'submodule', 'update', '--init', '--recursive'],
            env={}, cwd=self.path
        )
        to_delete = []
        for root, dirs, files in os.walk(self.path):
            for d in dirs:
                if d == '.git':
                    to_delete.append(os.path.join(root, d))
        for d in to_delete:
            shutil.rmtree(d)
        return self

    @classmethod
    def all_for_app(cls, app):
        try:
            files = os.listdir(os.path.join(
                options.BASEPATH, 'checkouts', app.repo.name, app.name
            ))
        except FileNotFoundError:
            return []
        for basename in files:
            f = os.path.join(
                options.BASEPATH, 'checkouts',
                app.repo.name, app.name, basename
            )
            if not os.path.isdir(f):
                continue
            name, commit = basename.split('-')
            yield cls(app, commit, name)

    def build(self):
        if 'before_build_cmd' in self.app.config:
            subprocess.check_call(
                self.app.config['before_build_cmd'],
                shell=True, cwd=self.path
            )
        for builder_cls in builders.__all__:
            builder = builder_cls(self)
            if builder.is_applicable:
                builder.build()
        if 'after_build_cmd' in self.app.config:
            subprocess.check_call(
                self.app.config['after_build_cmd'],
                shell=True, cwd=self.path
            )

    def remove(self):
        shutil.rmtree(self.path)
