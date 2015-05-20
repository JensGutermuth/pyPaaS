#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..repo import Repo
from .argparser import subparsers


def create(repo_name, ignore_existing=False):
    Repo.create(repo_name, ignore_existing)

repo_create_parser = subparsers.add_parser('repo:create')
repo_create_parser.add_argument('repo_name', type=str)
repo_create_parser.set_defaults(func=create)
