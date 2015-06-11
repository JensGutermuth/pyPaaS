#!/usr/bin/env python
"""
pyPaaS command line interface
"""

import subprocess
import sys

from .repo import Repo
from .sshkey import SSHKey


def print_usage_and_exit():
    print("""
Usage:
    pypaas git-receive-pack <repo_name>
    pypaas git-pre-receive-hook <repo_name>
    pypaas rebuild_authorized_keys
    pypaas rebuild [<repo_name> <branch>]
    pypaas list
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
    if len(sys.argv) < 2:
        print_usage_and_exit()

    if sys.argv[1] == 'git-receive-pack':
        if len(sys.argv) != 3:
            print_usage_and_exit()
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
        if len(sys.argv) != 3:
            print_usage_and_exit()
        repo = Repo(clean_repo_name(sys.argv[2]))
        for oldref, newref, refname in [l.split() for l in sys.stdin]:
            if not refname.startswith('refs/heads/'):
                sys.stderr.write(
                    'Your are pushing something other than a branch.\n' +
                    'Only branches are currently supported targets!\n'
                )
                sys.exit(1)
            branch = refname[len('refs/heads/'):]

            branches = []
            for r_branch in repo.branches.values():
                if r_branch.name == branch:
                    branches.append(r_branch)

            if len(branches) == 0:
                sys.stderr.write(
                    'This branch is not configured!\n'
                )
                sys.exit(1)

            for r_branch in branches:
                r_branch.deploy(newref)

    elif sys.argv[1] == 'rebuild_authorized_keys':
        if len(sys.argv) != 2:
            print_usage_and_exit()
        SSHKey.rebuild_authorized_keys()

    elif sys.argv[1] == 'rebuild':
        if len(sys.argv) not in [2, 4]:
            print_usage_and_exit()
        if len(sys.argv) == 4:
            repo = Repo(clean_repo_name(sys.argv[2]))
            branches = [repo.branches[clean_repo_name(sys.argv[3])]]
        else:
            branches = []
            for r in Repo.all():
                branches.extend(r.branches.values())
        for b in branches:
            if b.current_checkout is None:
                print('{b.repo.name}:{b.name} has no checkout. Skipping...'
                      .format(b=b))
                continue
            b.deploy(b.current_checkout.commit)

    elif sys.argv[1] == 'list':
        if len(sys.argv) != 2:
            print_usage_and_exit()
        print("\nRepos\n=====\n")
        for r in Repo.all():
            print('{}:'.format(r.name))
            for b in r.branches.values():
                print('\t{}:'.format(b.name))
                for runner in b.runners.values():
                    print('\t\t{r.name} ({r.cls_name})'
                          .format(r=runner))

    else:
        print_usage_and_exit()
