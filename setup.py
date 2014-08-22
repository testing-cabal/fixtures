#!/usr/bin/env python

from distutils.core import setup
import os.path

description = open(os.path.join(os.path.dirname(__file__), 'README'), 'rt').read()

setup(name="fixtures",
      version="0.3.16",
      description="Fixtures, reusable state for writing clean tests and more.",
      keywords="fixture fixtures unittest contextmanager",
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
          'Programming Language :: Python :: 3',
          'Topic :: Software Development :: Quality Assurance',
          'Topic :: Software Development :: Testing',
          ],
      requires = [
          'testtools',
          ],
      )
