#  fixtures: Fixtures with cleanups for testing and convenience.
#
# Copyright (c) 2010, Robert Collins <robertc@robertcollins.net>
# 
# Licensed under either the Apache License, Version 2.0 or the BSD 3-clause
# license at the users choice. A copy of both licenses are available in the
# project source as Apache-2.0 and BSD. You may not use this file except in
# compliance with one of these two licences.
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under these licenses is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# license you chose for the specific language governing permissions and
# limitations under that license.

import os.path

import testtools
from testtools.compat import _b

from fixtures import PythonPackage, TestWithFixtures


class TestPythonPackage(testtools.TestCase, TestWithFixtures):

    def test_has_tempdir(self):
        fixture = PythonPackage('foo', [])
        fixture.setUp()
        try:
            self.assertTrue(os.path.isdir(fixture.base))
        finally:
            fixture.cleanUp()
   
    def test_writes_package(self):
        fixture = PythonPackage('foo', [('bar.py', _b('woo'))])
        fixture.setUp()
        try:
            self.assertEqual('', open(os.path.join(fixture.base, 'foo',
                '__init__.py')).read())
            self.assertEqual('woo', open(os.path.join(fixture.base, 'foo',
                'bar.py')).read())
        finally:
            fixture.cleanUp()

    def test_no__init__(self):
        fixture = PythonPackage('foo', [('bar.py', _b('woo'))], init=False)
        fixture.setUp()
        try:
            self.assertFalse(os.path.exists(os.path.join(fixture.base, 'foo',
                '__init__.py')))
        finally:
            fixture.cleanUp()
