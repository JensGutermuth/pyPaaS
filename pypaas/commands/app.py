#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..app import App
from ..repo import Repo
from .argparser import subparsers


def create(name, repo_name, branch):
    App.create(name, Repo(repo_name), branch)

create_parser = subparsers.add_parser('app:create')
create_parser.add_argument('name', type=str)
create_parser.add_argument('repo_name', type=str)
create_parser.add_argument('branch', type=str,
                           nargs='?', default='master')
create_parser.set_defaults(func=create)


def remove(name):
    App.remove(name)

remove_parser = subparsers.add_parser('app:remove')
remove_parser.add_argument('name', type=str)
remove_parser.set_defaults(func=remove)


def set_env(app_name, name, value):
    app = App(app_name)
    if not app.config.has_section('env'):
        app.config.add_section('env')
    app.config.set('env', name, value)
    app.save_config()

set_env_parser = subparsers.add_parser('app:env:set')
set_env_parser.add_argument('app_name', type=str)
set_env_parser.add_argument('name', type=str)
set_env_parser.add_argument('value', type=str)
set_env_parser.set_defaults(func=set_env)


def get_env(app_name, name):
    app = App(app_name)
    print(app.config.get('env', name))

get_env_parser = subparsers.add_parser('app:env:get')
get_env_parser.add_argument('app_name', type=str)
get_env_parser.add_argument('name', type=str)
get_env_parser.set_defaults(func=get_env)


def get_all_env(app_name):
    app = App(app_name)
    print("\n".join("{}={}".format(k, app.config.get('env', k)) for k in
                    app.config.options('env')))

get_all_env_parser = subparsers.add_parser('app:env:get:all')
get_all_env_parser.add_argument('app_name', type=str)
get_all_env_parser.set_defaults(func=get_all_env)
