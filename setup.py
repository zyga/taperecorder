#!/usr/bin/env python
# Copyright 2013 Canonical Ltd.
# Written by:
#   Zygmunt Krynicki <zygmunt.krynicki@canonical.com>
#
# See COPYING for license information (LGPLv3)


from setuptools import setup


setup(
    name='taperecorder',
    version='0.1',
    author="Zygmunt Krynicki",
    author_email="zkrynicki@gmail.com",
    packages=['taperecorder'],
    url="https://github.com/zyga/taperecorder",
    test_suite='taperecorder.tests',
    entry_points={
        'console_scripts': [
            'taperecorder=taperecorder.main:main'
        ]
    })
