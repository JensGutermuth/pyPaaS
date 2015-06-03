#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import shutil
import subprocess
import sys

from .. import util
from .base import NginxBase


class NginxStatic(NginxBase):
    @property
    def nginx_location(self):
        return nginx_location.format(
            path=os.path.join(
                self.branch.current_checkout.path,
                subdirectory
            )
        )
