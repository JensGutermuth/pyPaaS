#!/usr/bin/env python
"""
pyPaaS command line interface
"""

import argparse
import subprocess
import sys

from .commands import app, git, repo, ssh
from .commands.argparser import parser


def clean_repo_name(repo_name):
    if not isinstance(repo_name, str):
        if len(repo_name) != 1:
            raise RuntimeError('More than one <repo_name>')
        repo_name = repo_name[0]

    if repo_name.startswith("'") and repo_name.endswith("'"):
        repo_name = repo_name[1:-1]
    return repo_name


def main():
    args = parser.parse_args()
    if hasattr(args, 'repo_name'):
        args.repo_name = clean_repo_name(args.repo_name)

    func = args.func
    dict_args = vars(args)
    del dict_args['func']
    func(**dict_args)
