#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from ..sshkey import SSHKey
from .argparser import subparsers


def add_key(name):
    SSHKey.create(name, sys.stdin.read())
    print("Successfully added key for", name)

add_key_parser = subparsers.add_parser('ssh:key:add')
add_key_parser.add_argument('name', type=str)
add_key_parser.set_defaults(func=add_key)
