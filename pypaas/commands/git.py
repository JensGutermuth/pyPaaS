#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import sys

from . import repo as repo_cmd
from ..app import App
from ..repo import Repo
from .argparser import subparsers


def receive_pack(repo_name):
    repo_cmd.create(repo_name, ignore_existing=True)
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

        apps = []
        for app in App.all():
            if app.config.get('repo', 'name') != repo.name:
                sys.stderr.write(type(app.config.get('repo', 'name')))
                continue
            if app.config.get('repo', 'branch') != branch:
                sys.stderr.write(type(app.config.get('repo', 'branch')))
                continue
            apps.append(app)
        if len(apps) == 0:
            sys.stderr.write(
                'No app configured for this branch!\n'
            )
            sys.exit(1)

        for app in apps:
            app.deploy(newref)

git_pre_receive_hook_parser = subparsers.add_parser('git-pre-receive-hook')
git_pre_receive_hook_parser.add_argument('repo_name', type=str)
git_pre_receive_hook_parser.set_defaults(func=pre_receive_hook)
