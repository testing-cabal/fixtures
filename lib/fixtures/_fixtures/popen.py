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

__all__ = [
    'PopenFixture'
    ]

import random
import subprocess

from fixtures import Fixture


class FakeProcess(object):
    """A test double process, roughly meeting subprocess.Popen's contract."""

    def __init__(self, args, info):
        self._args = args
        self.stdin = info.get('stdin')
        self.stdout = info.get('stdout')
        self.stderr = info.get('stderr')
        self.pid = random.randint(0, 65536)
        self.returncode = None

    def communicate(self):
        self.returncode = 0
        if self.stdout:
            out = self.stdout.getvalue()
        else:
            out = ''
        if self.stderr:
            err = self.stderr.getvalue()
        else:
            err = ''
        return out, err

    def wait(self):
        return self.returncode


class PopenFixture(Fixture):
    """Replace subprocess.Popen.

    Primarily useful for testing, this fixture replaces subprocess.Popen with a
    test double.

    :ivar procs: A list of the processes created by the fixture.
    """

    def __init__(self, get_info=lambda _:{}):
        """Create a PopenFixture

        :param get_info: Optional callback to control the behaviour of the
            created process. This callback takes a kwargs dict for the Popen
            call, and should return a dict with any desired attributes.
            e.g. return {'stdin': StringIO('foobar')}
        """
        self.get_info = get_info

    def setUp(self):
        super(PopenFixture, self).setUp()
        self.addCleanup(setattr, subprocess, 'Popen', subprocess.Popen)
        subprocess.Popen = self
        self.procs = []

    def __call__(self, args, bufsize=0, executable=None, stdin=None,
        stdout=None, stderr=None):
        proc_args = dict(args=args, bufsize=bufsize, executable=executable,
            stdin=stdin, stdout=stdout, stderr=stderr)
        proc_info = self.get_info(proc_args)
        result = FakeProcess(proc_args, proc_info)
        self.procs.append(result)
        return result
