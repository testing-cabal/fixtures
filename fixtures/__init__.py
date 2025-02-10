#  fixtures: Fixtures with cleanups for testing and convenience.
#
# Copyright (c) 2010, 2011, Robert Collins <robertc@robertcollins.net>
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


"""Fixtures provides a sensible contract for reusable test fixtures.

It also provides glue for using these in common test runners and acts as a
common repository for widely used Fixture classes.

See the README for a manual, and the docstrings on individual functions and
methods for details.

Most users will want to look at TestWithFixtures and Fixture, to start with.
"""

from fixtures._version import __version__

__all__ = [
    'ByteStream',
    'CompoundFixture',
    'DetailStream',
    'EnvironmentVariable',
    'EnvironmentVariableFixture',
    'FakeLogger',
    'FakePopen',
    'Fixture',
    'FunctionFixture',
    'LogHandler',
    'LoggerFixture',
    'MethodFixture',
    'MockPatch',
    'MockPatchMultiple',
    'MockPatchObject',
    'MonkeyPatch',
    'MultipleExceptions',
    'NestedTempfile',
    'PackagePathEntry',
    'PopenFixture',
    'PythonPackage',
    'PythonPathEntry',
    'SetupError',
    'StringStream',
    'TempDir',
    'TempHomeDir',
    'TestWithFixtures',
    'Timeout',
    'TimeoutException',
    'WarningsCapture',
    'WarningsFilter',
    '__version__',
]


from fixtures.fixture import (  # noqa: E402
    CompoundFixture,
    Fixture,
    FunctionFixture,
    MethodFixture,
    MultipleExceptions,
    SetupError,
)
from fixtures._fixtures import (  # noqa: E402
    ByteStream,
    DetailStream,
    EnvironmentVariable,
    EnvironmentVariableFixture,
    FakeLogger,
    FakePopen,
    LoggerFixture,
    LogHandler,
    MockPatch,
    MockPatchMultiple,
    MockPatchObject,
    MonkeyPatch,
    NestedTempfile,
    PackagePathEntry,
    PopenFixture,
    PythonPackage,
    PythonPathEntry,
    StringStream,
    TempDir,
    TempHomeDir,
    Timeout,
    TimeoutException,
    WarningsCapture,
    WarningsFilter,
)
from fixtures.testcase import TestWithFixtures  # noqa: E402


def test_suite():
    import fixtures.tests  # noqa: F401

    return fixtures.tests.test_suite()


def load_tests(loader, standard_tests, pattern):
    standard_tests.addTests(loader.loadTestsFromNames(["fixtures.tests"]))
    return standard_tests
