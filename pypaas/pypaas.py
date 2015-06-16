#!/usr/bin/env python
"""
pyPaaS command line interface
"""

import os.path
import subprocess
import sys

import flock

from .domain import Domain
from .repo import Repo
from .runners import SimpleProcess
from .sshkey import SSHKey


def print_usage_and_exit():
    print("""
Usage:
    pypaas git-receive-pack <repo_name>
    pypaas git-pre-receive-hook <repo_name>
    pypaas rebuild_authorized_keys
    pypaas rebuild [<repo_name> <branch>]
    pypaas list
    pypaas cleanup
    pypaas costum_cmds <repo_name> <branch> <cmd>...
""")
    sys.exit(1)


def clean_args(args):
    for a in args:
        if a.startswith("'") and a.endswith("'"):
            a = a[1:-1]
        yield a


def git_receive_pack(repo_name, lockfile):
    with flock.Flock(lockfile, flock.LOCK_EX | flock.LOCK_NB):
        repo = Repo(repo_name)

    # Will call pypaas git-pre-receive-hook
    # Would always fail if we still have the lock.
    subprocess.check_call(
        [
            "git-shell", "-c",
            "git-receive-pack '{}'".format(repo.path)
        ],
        stdout=None, stderr=None,
        stdin=None
    )


def git_pre_receive_hook(repo_name):
    repo = Repo(repo_name)
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


def rebuild(repo_name, branch):
    if repo_name is not None:
        repo = Repo(repo_name)
        branches = [repo.branches[branch]]
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


def cmd_list():
    print("\nRepos\n=====\n")
    for r in Repo.all():
        print('{}:'.format(r.name))
        for b in r.branches.values():
            print('\t{}:'.format(b.name))
            for runner in b.runners.values():
                print('\t\t{r.name} ({r.cls_name})'
                      .format(r=runner))


def cleanup():
    SimpleProcess.cleanup()
    Domain.cleanup()


def costum_cmds(repo, branch, cmds):
    branch = Repo(name).branches[branch]
    if branch.current_checkout is None:
        print('This repo has not been deployed yet. Please deploy first.')
        sys.exit(1)
    for c in cmds:
        branch.current_checkout.run_costum_cmd(c)


def main():
    with open(os.path.expanduser('~/.pypaas-lock'), 'w') as f:
        try:
            args = list(clean_args(sys.argv))

            if len(args) < 2:
                print_usage_and_exit()

            # This is a special case: It calls git-shell, which in turn
            # will call pypaas git-pre-receive-hook. If we take the lock here,
            # git-pre-receive-hook will always fail.
            # git_receive_pack takes the lock as long as possible.
            if args[1] == 'git-receive-pack':
                if len(args) != 3:
                    print_usage_and_exit()
                git_receive_pack(args[2], lockfile=f)
                return

            # This lock prevents two instances of pypaas from running
            # concurrently.
            # This is very important: pypaas is not designed to handle
            # a second process changing state as well. Replacing a files
            # (for example) is crash-safe, but not concurrency-safe,
            # as you can overwrite stuff without even realizing.
            # Finer grained locking is not inherently impossible, it's just
            # a source of significant complexity and potential for non-obvious
            # and subtile bugs.
            with flock.Flock(f, flock.LOCK_EX | flock.LOCK_NB):
                if args[1] == 'git-pre-receive-hook':
                    if len(args) != 3:
                        print_usage_and_exit()
                    git_pre_receive_hook(args[2])

                elif args[1] == 'rebuild_authorized_keys':
                    if len(args) != 2:
                        print_usage_and_exit()
                    SSHKey.rebuild_authorized_keys()

                elif args[1] == 'rebuild':
                    if len(args) not in [2, 4]:
                        print_usage_and_exit()
                    if len(args) == 4:
                        rebuild(args[2], args[3])
                    else:
                        rebuild(None, None)

                elif args[1] == 'list':
                    if len(args) != 2:
                        print_usage_and_exit()
                    cmd_list()

                elif args[1] == 'cleanup':
                    if len(args) != 2:
                        print_usage_and_exit()
                    cleanup()

                elif args[1] == 'costum_cmds':
                    if len(args) < 5:
                        print_usage_and_exit()
                    costum_cmds(args[2], args[3], args[4:])

                else:
                    print_usage_and_exit()
        except BlockingIOError:
            sys.stderr.write(
                'pypaas is already running. Please try again later.'
            )
            sys.stderr.flush()
            sys.exit(1)
