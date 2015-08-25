#!/usr/bin/env python
# -*- coding: utf -*-
import os
import os.path

from setuptools import find_packages, setup

install_requires = [
    'PyYAML>=3.11',
    'flock>=0.1'
]

setup(
    name='pyPaaS',
    version='0.3.0',
    author="Jens Gutermuth, Fintura GmbH",
    author_email="jens.gutermuth@fintura.de",
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'pypaas=pypaas.pypaas:main',
        ]
    }
)
