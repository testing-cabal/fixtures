#!/usr/bin/env python

from distutils.core import setup
import os.path

description = file(os.path.join(os.path.dirname(__file__), 'README'), 'rb').read()

setup(name="fixtures",
      version="0.3.7",
      description="Fixtures, reusable state for writing clean tests and more.",
      long_description=description,
      maintainer="Robert Collins",
      maintainer_email="robertc@robertcollins.net",
      url="https://launchpad.net/python-fixtures",
      packages=['fixtures', 'fixtures._fixtures', 'fixtures.tests',
        'fixtures.tests._fixtures'],
      package_dir = {'':'lib'},
      classifiers = [
          'Development Status :: 6 - Mature',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'License :: OSI Approved :: Apache Software License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Software Development :: Quality Assurance',
          'Topic :: Software Development :: Testing',
          ],
      )
