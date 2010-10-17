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

import os

import testtools

import fixtures
from fixtures import EnvironmentVariableFixture, TestWithFixtures


class TestEnvironmentVariableFixture(testtools.TestCase, TestWithFixtures):

    def test_setup_ignores_missing(self):
        fixture = EnvironmentVariableFixture('FIXTURES_TEST_VAR')
        os.environ.pop('FIXTURES_TEST_VAR', '')
        self.useFixture(fixture)
        self.assertEqual(None, os.environ.get('FIXTURES_TEST_VAR'))

    def test_setup_sets_when_missing(self):
        fixture = EnvironmentVariableFixture('FIXTURES_TEST_VAR', 'bar')
        os.environ.pop('FIXTURES_TEST_VAR', '')
        self.useFixture(fixture)
        self.assertEqual('bar', os.environ.get('FIXTURES_TEST_VAR'))

    def test_setup_deletes(self):
        fixture = EnvironmentVariableFixture('FIXTURES_TEST_VAR')
        os.environ['FIXTURES_TEST_VAR'] = 'foo'
        self.useFixture(fixture)
        self.assertEqual(None, os.environ.get('FIXTURES_TEST_VAR'))

    def test_setup_overrides(self):
        fixture = EnvironmentVariableFixture('FIXTURES_TEST_VAR', 'bar')
        os.environ['FIXTURES_TEST_VAR'] = 'foo'
        self.useFixture(fixture)
        self.assertEqual('bar', os.environ.get('FIXTURES_TEST_VAR'))

    def test_cleanup_deletes_when_missing(self):
        fixture = EnvironmentVariableFixture('FIXTURES_TEST_VAR')
        os.environ.pop('FIXTURES_TEST_VAR', '')
        with fixture:
            os.environ['FIXTURES_TEST_VAR'] = 'foo'
        self.assertEqual(None, os.environ.get('FIXTURES_TEST_VAR'))
        
    def test_cleanup_deletes_when_set(self):
        fixture = EnvironmentVariableFixture('FIXTURES_TEST_VAR', 'bar')
        os.environ.pop('FIXTURES_TEST_VAR', '')
        with fixture:
            os.environ['FIXTURES_TEST_VAR'] = 'foo'
        self.assertEqual(None, os.environ.get('FIXTURES_TEST_VAR'))

    def test_cleanup_restores_when_missing(self):
        fixture = EnvironmentVariableFixture('FIXTURES_TEST_VAR')
        os.environ['FIXTURES_TEST_VAR'] = 'bar'
        with fixture:
            os.environ.pop('FIXTURES_TEST_VAR', '')
        self.assertEqual('bar', os.environ.get('FIXTURES_TEST_VAR'))
        
    def test_cleanup_restores_when_set(self):
        fixture = EnvironmentVariableFixture('FIXTURES_TEST_VAR')
        os.environ['FIXTURES_TEST_VAR'] = 'bar'
        with fixture:
            os.environ['FIXTURES_TEST_VAR'] = 'quux'
        self.assertEqual('bar', os.environ.get('FIXTURES_TEST_VAR'))
