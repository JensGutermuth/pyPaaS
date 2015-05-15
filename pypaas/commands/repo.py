#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..repo import Repo
from .argparser import subparsers


def create(repo_name, fail_if_preexisting=True):
    repo = Repo(repo_name)
    repo.ensure_existence(fail_if_preexisting=fail_if_preexisting)

repo_create_parser = subparsers.add_parser('repo:create')
repo_create_parser.add_argument('repo_name', type=str)
repo_create_parser.set_defaults(func=create)


def checkout_and_build(repo_name, commitish, name):
    repo = Repo(repo_name)
    checkout = repo.new_checkout(commitish, name)
    checkout.build()

repo_checkout_and_build_parser = \
    subparsers.add_parser('repo:checkout-and-build')
repo_checkout_and_build_parser.add_argument('repo_name', type=str)
repo_checkout_and_build_parser.add_argument('commitish', type=str)
repo_checkout_and_build_parser.add_argument('name', type=str)
repo_checkout_and_build_parser.set_defaults(func=checkout_and_build)
