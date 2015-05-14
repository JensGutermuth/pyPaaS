#!/usr/bin/env python
"""
Usage:
    pypaas git-receive-pack <repo_name>
    pypaas git-pre-receive-hook <repo_name>
"""

import subprocess
import sys

from docopt import docopt

from .repo import Repo


def clean_repo_name(args):
    repo_name = args["<repo_name>"]
    if repo_name.startswith("'") and repo_name.endswith("'"):
        repo_name = repo_name[1:-1]
    return repo_name


def main():
    args = docopt(__doc__)

    if args["git-receive-pack"]:
        repo = Repo(clean_repo_name(args))
        repo.ensure_existence()
        subprocess.check_call(
            [
                "git-shell", "-c",
                "git-receive-pack '{}'".format(repo.path)
            ],
            stdout=None, stderr=None,
            stdin=None
        )

    elif args['git-pre-receive-hook']:
        repo = Repo(clean_repo_name(args))
        for oldref, newref, refname in [l.split() for l in sys.stdin]:
            if not refname.startswith('refs/heads/'):
                sys.stderr.write(
                    'Your are pushing something other than a branch.\n' +
                    'Only branches are currently supported targets!\n'
                )
                sys.exit(1)
            branch = refname[len('refs/heads/'):]
            if branch != 'master':
                sys.stderr.write(
                    'Only pushing to master is currently supported!\n'
                )
                sys.exit(1)
            checkout = repo.new_checkout(newref, branch)
            checkout.build()
    else:
        raise RuntimeError('No command executed, very fishy!')
