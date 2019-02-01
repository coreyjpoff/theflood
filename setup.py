#!/usr/bin/env python2.7

from setuptools import setup

setup(
    name='theflood',
    packages=['theflood'],
    include_package_data=True,
    install_requires=[
        'flask',
        'floodmodel',
    ],
)
