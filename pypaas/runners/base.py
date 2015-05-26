#!/usr/bin/env python
# -*- coding: utf-8 -*-


class BaseRunner(object):
    def __init__(self, app):
        self.app = app

    @property
    def is_applicable(self):
        """
        Looks at the checkout and determines, if this runner is applicable to
        the code.
        """
        raise NotImplemented()

    def create(self):
        raise NotImplemented

    def start(self):
        raise NotImplemented

    def stop(self):
        raise NotImplemented

    def destroy(self):
        raise NotImplemented
