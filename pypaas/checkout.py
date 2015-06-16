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
    def __init__(self, branch, commit, name):
        self.branch, self.commit, self.name = branch, commit, name

    @property
    def path(self):
        return os.path.join(
            options.BASEPATH, 'checkouts',
            self.branch.repo.name, self.branch.name,
            '{}-{}'.format(self.name, self.commit[:11])
        )

    @classmethod
    def create(cls, branch, commit):
        name = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        self = cls(branch, commit, name)
        subprocess.check_call(
            ['git', 'clone', '-q', self.branch.repo.path, self.path],
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

    @property
    def cmd_env(self):
        env = self.branch.config.get('env', dict())
        env.update(os.environ)
        return env

    @classmethod
    def all_for_branch(cls, branch):
        try:
            files = os.listdir(os.path.join(
                options.BASEPATH, 'checkouts', branch.repo.name, branch.name
            ))
        except FileNotFoundError:
            return []
        for basename in files:
            f = os.path.join(
                options.BASEPATH, 'checkouts',
                branch.repo.name, branch.name, basename
            )
            if not os.path.isdir(f):
                continue
            name, commit = basename.split('-')
            yield cls(branch, commit, name)

    def run_hook_cmd(self, name):
        try:
            hook = self.branch.config['hooks'][name]
        except KeyError:
            return
        if not isinstance(hook, list):
            hook = [hook]
        for c in hook:
            subprocess.check_call(c, shell=True, cwd=self.path,
                                  env=self.cmd_env)

    @property
    def costum_cmds(self):
        try:
            return self.branch.config['costum_cmds']
        except KeyError:
            return dict()

    def run_costum_cmd(self, name):
        subprocess.check_call(
            self.costum_cmds[name],
            shell=True, cwd=self.path,
            env=self.cmd_env
        )

    def build(self):
        self.run_hook_cmd('before_build')
        for builder_cls in builders.__all__:
            builder = builder_cls(self)
            if builder.is_applicable:
                builder.build()
        self.run_hook_cmd('after_build')

    def remove(self):
        shutil.rmtree(self.path)
