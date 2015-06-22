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

__all__ = [
    'FakePopen',
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
        self._returncode = info.get('returncode', 0)
        self.returncode = None

    def communicate(self):
        self.returncode = self._returncode
        if self.stdout:
            out = self.stdout.getvalue()
        else:
            out = ''
        if self.stderr:
            err = self.stderr.getvalue()
        else:
            err = ''
        return out, err

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.wait()

    def kill(self):
        pass

    def wait(self, timeout=None, endtime=None):
        if self.returncode is None:
            self.communicate()
        return self.returncode


class FakePopen(Fixture):
    """Replace subprocess.Popen.

    Primarily useful for testing, this fixture replaces subprocess.Popen with a
    test double.

    :ivar procs: A list of the processes created by the fixture.
    """

    _unpassed = object()

    def __init__(self, get_info=lambda _:{}):
        """Create a PopenFixture

        :param get_info: Optional callback to control the behaviour of the
            created process. This callback takes a kwargs dict for the Popen
            call, and should return a dict with any desired attributes.
            Only parameters that are supplied to the Popen call are in the
            dict, making it possible to detect the difference between 'passed
            with a default value' and 'not passed at all'.

            e.g. 
            def get_info(proc_args):
                self.assertEqual(subprocess.PIPE, proc_args['stdin'])
                return {'stdin': StringIO('foobar')}

            The default behaviour if no get_info is supplied is for the return
            process to have returncode of None, empty streams and a random pid.
        """
        super(FakePopen, self).__init__()
        self.get_info = get_info

    def _setUp(self):
        self.addCleanup(setattr, subprocess, 'Popen', subprocess.Popen)
        subprocess.Popen = self
        self.procs = []

    # The method has the correct signature so we error appropriately if called
    # wrongly.
    def __call__(self, args, bufsize=_unpassed, executable=_unpassed,
        stdin=_unpassed, stdout=_unpassed, stderr=_unpassed,
        preexec_fn=_unpassed, close_fds=_unpassed, shell=_unpassed,
        cwd=_unpassed, env=_unpassed, universal_newlines=_unpassed,
        startupinfo=_unpassed, creationflags=_unpassed):
        proc_args = dict(args=args)
        local = locals()
        for param in [
            "bufsize", "executable", "stdin", "stdout", "stderr",
            "preexec_fn", "close_fds", "shell", "cwd", "env",
            "universal_newlines", "startupinfo", "creationflags"]:
            if local[param] is not FakePopen._unpassed:
                proc_args[param] = local[param]
        proc_info = self.get_info(proc_args)
        result = FakeProcess(proc_args, proc_info)
        self.procs.append(result)
        return result


PopenFixture = FakePopen
