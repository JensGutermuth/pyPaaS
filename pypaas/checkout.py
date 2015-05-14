#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import shutil
import subprocess

from . import options


class Checkout(object):
    def __init__(self, repo, commit, name):
        self.repo, self.commit, self.name = repo, commit, name

    @property
    def path(self):
        return os.path.join(
            options.BASEPATH, self.repo.name,
            'checkouts', '{}-{}'.format(self.name, self.commit)
        )

    def ensure_existence(self):
        if not os.path.isdir(self.path):
            subprocess.check_call(
                ['git', 'clone', '-q', self.repo.path, self.path],
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
