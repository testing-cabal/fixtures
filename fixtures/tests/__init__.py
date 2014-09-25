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

import doctest
import sys
import unittest

import fixtures.tests._fixtures


def test_suite():
    standard_tests = unittest.TestSuite()
    loader = unittest.TestLoader()
    return load_tests(loader, standard_tests, None)


def load_tests(loader, standard_tests, pattern):
    test_modules = [
        'callmany',
        'fixture',
        'testcase',
        ]
    prefix = "fixtures.tests.test_"
    test_mod_names = [prefix + test_module for test_module in test_modules]
    standard_tests.addTests(loader.loadTestsFromNames(test_mod_names))
    if sys.version_info >= (2, 7):
        # 2.7 calls load_tests for us
        standard_tests.addTests(loader.loadTestsFromName('fixtures.tests._fixtures'))
    else:
        # We need to call it ourselves.
        standard_tests.addTests(fixtures.tests._fixtures.load_tests(
            loader, loader.loadTestsFromName('fixtures.tests._fixtures'), pattern))
    doctest.set_unittest_reportflags(doctest.REPORT_ONLY_FIRST_FAILURE)
    standard_tests.addTest(doctest.DocFileSuite("../../README"))
    return standard_tests
