#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import shutil
import stat
import subprocess

from . import options, runners, util
from .checkout import Checkout


class App(object):
    """
    Represents a group of processes running code from a specific branch from a
    repo.
    """
    def __init__(self, repo, name, config):
        self.repo = repo
        self.config = config
        self.name = name
        util.mkdir_p(self.state_path)

    @property
    def state_path(self):
        return os.path.join(
            options.BASEPATH, 'apps', self.repo.name, self.name,
        )

    @property
    def current_checkout(self):
        # used during startup
        if hasattr(self, '_current_checkout'):
            return self._current_checkout

        try:
            with open(os.path.join(self.state_path, 'current_checkout')) as f:
                name = f.read()
        except IOError:
            return None
        for c in Checkout.all_for_app(self):
            if c.name == name:
                return c
        # apparrently that checkout does not exist
        os.unlink(os.path.join(self.state_path, 'current_checkout'))
        return None

    @property
    def branch(self):
        return self.config['branch']

    @property
    def runners(self):
        for runner_cls in runners.__all__:
            runner = runner_cls(self)
            if runner.is_applicable:
                yield runner

    def deploy(self, commit):
        new_checkout = Checkout.create(self, commit)
        new_checkout.build()

        for runner in self.runners:
            runner.stop()

        if 'migration_cmd' in self.config:
            subprocess.check_call(
                self.config['migration_cmd'],
                shell=True, cwd=new_checkout.path,
                env=self.config['env']
            )

        self._current_checkout = new_checkout
        for runner in self.runners:
            runner.configure()
            runner.start()

        # TODO: health checks

        del self._current_checkout
        util.replace_file(
            os.path.join(self.state_path, 'current_checkout'),
            new_checkout.name
        )

        for c in Checkout.all_for_app(self):
            if c.name != new_checkout.name:
                c.remove()
