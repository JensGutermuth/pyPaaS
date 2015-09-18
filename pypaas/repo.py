#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import stat
import subprocess
import sys

from . import options, util
from .branch import Branch
from .checkout import Checkout


HOOKSCRIPT = """
#!/usr/bin/env bash
set -e; set -o pipefail;
export PATH=$PATH:{path_suffix}
cat | logging_wrapper pypaas git-pre-receive-hook {repo.name}
""".strip()


class Repo(object):
    """
    A git repository.

    This is the canonical storage of source code and the only way to get code
    into pyPaaS or update it.
    """
    def __init__(self, name):
        self.name = name
        if self.name not in options.repos:
            raise ValueError('This repo is not configured')

        if not os.path.isdir(os.path.join(self.path, 'refs/heads')):
            util.mkdir_p(os.path.join(options.BASEPATH, 'repos'))
            subprocess.check_output(['git', 'init', '--bare', self.path])
            self.write_hook()

    @property
    def config(self):
        return options.repos[self.name]

    @property
    def path(self):
        return os.path.join(options.BASEPATH, 'repos', self.name)

    @property
    def branches(self):
        return dict((name, Branch(self, name, branch_config))
                    for name, branch_config in self.config['branches'].items())

    @classmethod
    def all(cls):
        for name in options.repos:
            yield cls(name)

    def write_hook(self):
        hook = os.path.join(self.path, 'hooks/pre-receive')
        with open(hook, 'w') as hookf:
            hookf.write(HOOKSCRIPT.format(
                repo=self, path_suffix=os.path.dirname(sys.executable)
            ))
        os.chmod(hook, stat.S_IXUSR | os.stat(hook).st_mode)
