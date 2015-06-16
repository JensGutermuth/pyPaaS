#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import shutil
import stat
import subprocess
import sys

from . import options, runners, util
from .checkout import Checkout


class Branch(object):
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
            options.BASEPATH, 'state', self.repo.name, self.name,
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
        for c in Checkout.all_for_branch(self):
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
        res = dict()
        for name, config in self.config['runners'].items():
            for runner_cls in runners.__all__:
                if runner_cls.__name__ == config['type']:
                    res[name] = runner_cls(name, self, config)
                    break
            else:
                raise ValueError('Runner type {} is unknown'
                                 .format(config['type']))
        return res

    def deploy(self, commit):
        # Has to here. repo -> branch -> domain -> repo is a circle otherwise
        from .domain import Domain

        new_checkout = Checkout.create(self, commit)
        new_checkout.build()

        for runner in self.runners.values():
            runner.enable_maintenance()
        Domain.configure_all()

        new_checkout.run_hook_cmd('maintenance')

        self._current_checkout = new_checkout
        for runner in self.runners.values():
            runner.disable_maintenance()

        # TODO: health checks

        del self._current_checkout
        util.replace_file(
            os.path.join(self.state_path, 'current_checkout'),
            new_checkout.name
        )

        Domain.configure_all()

        for c in Checkout.all_for_branch(self):
            if c.name != new_checkout.name:
                c.remove()
