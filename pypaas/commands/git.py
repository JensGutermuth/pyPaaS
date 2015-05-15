#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import sys

from . import repo as repo_cmd
from ..repo import Repo
from .argparser import subparsers


def receive_pack(repo_name):
    repo_cmd.create(repo_name, fail_if_preexisting=False)
    subprocess.check_call(
        [
            "git-shell", "-c",
            "git-receive-pack '{}'".format(Repo(repo_name).path)
        ],
        stdout=None, stderr=None,
        stdin=None
    )

git_receive_pack_parser = subparsers.add_parser('git-receive-pack')
git_receive_pack_parser.add_argument('repo_name', type=str)
git_receive_pack_parser.set_defaults(func=receive_pack)


def pre_receive_hook(repo_name):
    repo = Repo(repo_name)
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
        repo_cmd.checkout_and_build(repo_name, newref, branch)

git_pre_receive_hook_parser = subparsers.add_parser('git-pre-receive-hook')
git_pre_receive_hook_parser.add_argument('repo_name', type=str)
git_pre_receive_hook_parser.set_defaults(func=pre_receive_hook)
