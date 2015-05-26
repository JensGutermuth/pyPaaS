#!/usr/bin/env python
"""
pyPaaS command line interface
"""

import subprocess
import sys

from .app import App
from .repo import Repo


def print_usage_and_exit():
    print("""
Usage:
    pypaas git-receive-pack <repo_name>
    pypaas git-pre-receive-hook <repo_name>
""")
    sys.exit(1)


def clean_repo_name(repo_name):
    if not isinstance(repo_name, str):
        if len(repo_name) != 1:
            raise RuntimeError('More than one <repo_name>')
        repo_name = repo_name[0]

    if repo_name.startswith("'") and repo_name.endswith("'"):
        repo_name = repo_name[1:-1]
    return repo_name


def main():
    sys.stderr.write(repr(sys.argv))
    if len(sys.argv) != 3:
        print_usage_and_exit()

    if sys.argv[1] == 'git-receive-pack':
        repo = Repo(clean_repo_name(sys.argv[2]))
        subprocess.check_call(
            [
                "git-shell", "-c",
                "git-receive-pack '{}'".format(repo.path)
            ],
            stdout=None, stderr=None,
            stdin=None
        )
    elif sys.argv[1] == 'git-pre-receive-hook':
        repo = Repo(clean_repo_name(sys.argv[2]))
        for oldref, newref, refname in [l.split() for l in sys.stdin]:
            if not refname.startswith('refs/heads/'):
                sys.stderr.write(
                    'Your are pushing something other than a branch.\n' +
                    'Only branches are currently supported targets!\n'
                )
                sys.exit(1)
            branch = refname[len('refs/heads/'):]

            apps = []
            for app in repo.apps:
                if app.branch == branch:
                    apps.append(app)

            if len(apps) == 0:
                sys.stderr.write(
                    'No app configured for this branch!\n'
                )
                sys.exit(1)

            for app in apps:
                app.deploy(newref)
    else:
        print_usage_and_exit()
