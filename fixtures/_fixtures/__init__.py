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


"""Included fixtures."""

__all__ = [
    'ByteStream',
    'DetailStream',
    'EnvironmentVariable',
    'EnvironmentVariableFixture',
    'FakeLogger',
    'FakePopen',
    'LoggerFixture',
    'LogHandler',
    'MockPatch',
    'MockPatchMultiple',
    'MockPatchObject',
    'MonkeyPatch',
    'NestedTempfile',
    'PackagePathEntry',
    'PopenFixture',
    'PythonPackage',
    'PythonPathEntry',
    'StringStream',
    'TempDir',
    'TempHomeDir',
    'Timeout',
    'TimeoutException',
    'WarningsCapture',
    ]


from fixtures._fixtures.environ import (
    EnvironmentVariable,
    EnvironmentVariableFixture,
    )
from fixtures._fixtures.logger import (
    FakeLogger,
    LoggerFixture,
    LogHandler,
    )
from fixtures._fixtures.mockpatch import (
    MockPatch,
    MockPatchMultiple,
    MockPatchObject,
    )
from fixtures._fixtures.monkeypatch import MonkeyPatch
from fixtures._fixtures.popen import (
    FakePopen,
    PopenFixture,
    )
from fixtures._fixtures.packagepath import PackagePathEntry
from fixtures._fixtures.pythonpackage import PythonPackage
from fixtures._fixtures.pythonpath import PythonPathEntry
from fixtures._fixtures.streams import (
    ByteStream,
    DetailStream,
    StringStream,
    )
from fixtures._fixtures.tempdir import (
    NestedTempfile,
    TempDir,
    )
from fixtures._fixtures.temphomedir import (
    TempHomeDir,
    )
from fixtures._fixtures.timeout import (
    Timeout,
    TimeoutException,
    )
from fixtures._fixtures.warnings import (
    WarningsCapture,
    )
