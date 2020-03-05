#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path

import yaml

from . import options, util


class Port(object):
    def __init__(self, runner, port=None):
        if port is None:
            # find a free port
            state = self.get_state()
            port_min = options.main['ports']['min']
            port_max = options.main['ports']['max']
            for p in range(port_min, port_max):
                if p not in state:
                    self.port = p
                    state[p] = dict(
                        runner_type=runner.__class__.__name__,
                        branch=runner.branch.name,
                        repo=runner.branch.repo.name
                    )
                    break
            else:
                raise RuntimeError('could not find a free port')
            self.set_state(state)
        else:
            self.port = port
        self.runner = runner

    def free(self):
        state = self.get_state()
        pstate = state[self.port]
        assert pstate['runner_type'] == self.runner.__class__.__name__
        assert pstate['branch'] == self.runner.branch.name
        assert pstate['repo'] == self.runner.branch.repo.name
        del state[self.port]
        self.set_state(state)

    @classmethod
    def all_for_runner(cls, runner):
        state = cls.get_state()
        for p, v in state.items():
            if not all(key in v for key in ['runner_type', 'branch', 'repo']):
                # broken or old entry?
                continue
            if v['runner_type'] == runner.__class__.__name__ and \
                    v['branch'] == runner.branch.name and \
                    v['repo'] == runner.branch.repo.name:
                yield cls(runner, p)

    @staticmethod
    def get_state():
        try:
            state = yaml.load(open(os.path.expanduser('~/ports.yml')), Loader=yaml.FullLoader)
            return state if state is not None else {}
        except FileNotFoundError:
            return {}

    @staticmethod
    def set_state(new_state):
        util.replace_file(os.path.expanduser('~/ports.yml'),
                          yaml.dump(new_state))
