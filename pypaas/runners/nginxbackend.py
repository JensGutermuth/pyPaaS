#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import os
import os.path
import shutil
import subprocess
import sys

from .. import util
from ..portallocator import Port
from .base import NginxBase
from .simpleprocess import SimpleProcess

upstream = "    server {host}:{port};"

nginx_conf = """
upstream backend_{name} {{
{extra_upstream_config}
{upstreams}
}}
"""

nginx_location = """
    proxy_pass http://backend_{name};
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header Host $http_host;
    {extra_config}
"""


class NginxBackend(SimpleProcess, NginxBase):
    def get_process_env(self, idx, **kwargs):
        env = copy.deepcopy(super().get_process_env(idx=idx, **kwargs))
        self.new_ports.append(Port(self))
        env['PORT'] = self.new_ports[-1].port
        return env

    def configure(self):
        self.new_ports = []
        old_ports = list(Port.all_for_runner(self))
        print('old_ports', repr([p.port for p in old_ports]))
        super().configure()
        for p in old_ports:
            p.free()

    def deconfigure(self):
        old_ports = list(Port.all_for_runner(self))
        for p in old_ports:
            p.free()

    @property
    def nginx_location(self):
        return nginx_location.format(
            name=self.name,
            extra_config=self.branch.config['runners'][self._name]
                             .get('nginx_extra_config', '')
        )

    @property
    def nginx_conf(self):
        return nginx_conf.format(
            name=self.name,
            upstreams='\n'.join(
                upstream.format(
                    host='127.0.0.1',
                    port=p.port,
                ) for p in Port.all_for_runner(self)
            ),
            extra_upstream_config=self.branch.config.get(
                'nginx_extra_upstream_config',
                ''
            )
        )
