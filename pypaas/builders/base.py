#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os


class BaseBuilder(object):
    def __init__(self, checkout):
        self.checkout = checkout

    @property
    def is_applicable(self):
        """
        Looks at the checkout and determines, if this builder is applicable to
        the code. A python builder could for example check for a setup.py file.
        """
        raise NotImplemented()

    def build(self):
        """Execute the build process"""
        raise NotImplemented()
