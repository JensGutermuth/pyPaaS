#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..app import App
from ..repo import Repo
from .argparser import subparsers


def create(name, repo_name, branch):
    App.create(name, Repo(repo_name), branch)

repo_create_parser = subparsers.add_parser('app:create')
repo_create_parser.add_argument('name', type=str)
repo_create_parser.add_argument('repo_name', type=str)
repo_create_parser.add_argument('branch', type=str,
                                nargs='?', default='master')
repo_create_parser.set_defaults(func=create)


def remove(name):
    App.remove(name)

repo_remove_parser = subparsers.add_parser('app:remove')
repo_remove_parser.add_argument('name', type=str)
repo_remove_parser.set_defaults(func=remove)
