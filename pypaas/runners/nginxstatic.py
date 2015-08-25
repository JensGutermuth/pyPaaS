#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import shutil
import subprocess
import sys

from .. import util
from .base import NginxBase


nginx_location = """
    alias {path}/;
"""


class NginxStatic(NginxBase):
    @property
    def nginx_location(self):
        subdirectory = self.config.get('subdirectory', '')
        while len(subdirectory) > 0 and subdirectory[0] == '/':
            subdirectory = subdirectory[1:]
        while len(subdirectory) > 0 and subdirectory[-1] == '/':
            subdirectory = subdirectory[:-1]

        return nginx_location.format(
            path=os.path.join(
                self.branch.current_checkout.path,
                subdirectory
            )
        )
