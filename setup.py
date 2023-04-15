#!/usr/bin/env python

"""
# Tinta
# Copyright 2023 github.com/brandoncript

# This program is bound to the Hippocratic License 2.1
# Full text is available here:
# https://firstdonoharm.dev/version/2/1/license

# Further to adherence to the Hippocratic Licenese, permission is hereby
# granted, free of charge, to any person obtaining a copy of this software
# and associated documentation files (the "Software") under the terms of the
# MIT License to deal in the Software without restriction, including without
# limitation the rights to use, copy, modify, merge, publish, distribute,
# sublicense, and / or sell copies of the Software, and to permit persons
# to whom the Software is furnished to do so, subject to the conditions layed
# out in the MIT License.

# Where a conflict or dispute would arise between these two licenses, HLv2.1
# shall take precedence.
"""

from pathlib import Path

from setuptools import setup

with Path('README.md').open(encoding='utf-8') as f:
    long_description = f.read()

setup(name='tinta',
      version='0.1.5b2',
      description='Tinta, a magical console output tool.',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='http://github.com/brandonscript/tinta',
      author='Brandon Shelley',
      author_email='brandon@pacificaviator.co',
      install_requires=['ansicolors'],
      include_package_data=True,
      license='MIT',
      packages=['tinta'],
      keywords='console colors ansi print terminal development',
      python_requires='>=3.6',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Environment :: Console',
          'Topic :: Utilities',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 3.8',
          'Programming Language :: Python :: 3.9',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11'
      ],
      zip_safe=False)
