#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import shutil
import stat
import subprocess

from configparser import ConfigParser

from . import options
from .checkout import Checkout
from .repo import Repo


class App(object):
    """
    Represents a group of processes running code from a specific branch from a
    repo.
    """
    def __init__(self, name):
        self.name = name
        self.config = ConfigParser()
        # Makes keys in config files case sensitive
        self.config.optionxform = str
        self.config.read(os.path.join(self.path, 'config.ini'))

    @property
    def path(self):
        return os.path.join(options.BASEPATH, 'apps', self.name)

    @property
    def repo(self):
        return Repo(self.config.get('repo', 'name'))

    @classmethod
    def all(cls):
        try:
            files = os.listdir(os.path.join(options.BASEPATH, 'apps'))
        except FileNotFoundError:
            return []
        for basename in files:
            f = os.path.join(options.BASEPATH, 'apps', basename)
            if not os.path.isdir(f):
                continue
            yield cls(basename)

    @classmethod
    def create(cls, name, repo, branch='master', ignore_existing=False):
        path = os.path.join(options.BASEPATH, 'apps', name)
        if os.path.isdir(path) and not ignore_existing:
            raise ValueError('This app already exists')

        if not os.path.isdir(path):
            subprocess.check_call(['mkdir', '-p', path])
            open(os.path.join(path, 'config.ini'), 'w').close()
            app = cls(name)
            app.config.add_section('repo')
            app.config.set('repo', 'name', repo.name)
            app.config.set('repo', 'branch', branch)
            app.save_config()
        else:
            app = cls(name)

        return app

    @classmethod
    def remove(cls, name):
        """
        Removes an app.

        If the app exists, this removes all traces even if the app is damaged
        (like has no or a broken config file).
        """
        # TODO: stop running processes
        shutil.rmtree(os.path.join(options.BASEPATH, 'apps', name))

    def save_config(self):
        self.config.write(open(os.path.join(self.path, 'config.ini'), 'w'))

    def deploy(self, commit):
        new_checkout = Checkout.create(self, commit)
        new_checkout.build()
        # TODO: enabling maintenance mode
        for checkout in Checkout.all_for_app(self):
            if checkout.name == new_checkout.name:
                continue
            for runner in checkout.runners:
                runner.destroy()

        # TODO: running migrations
        for runner in new_checkout.runners:
            runner.create()
        # TODO: health checks
        # TODO: write current version to config file
        # TODO: cleanup of old version
