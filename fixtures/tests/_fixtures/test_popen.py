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

import inspect
import io
import subprocess
import sys

import testtools

from fixtures import FakePopen, TestWithFixtures
from fixtures._fixtures.popen import FakeProcess


class TestFakePopen(testtools.TestCase, TestWithFixtures):

    def test_installs_restores_global(self):
        fixture = FakePopen()
        popen = subprocess.Popen
        fixture.setUp()
        try:
            self.assertEqual(subprocess.Popen, fixture)
        finally:
            fixture.cleanUp()
            self.assertEqual(subprocess.Popen, popen)

    def test___call___is_recorded(self):
        fixture = self.useFixture(FakePopen())
        proc = fixture(['foo', 'bar'], 1, None, 'in', 'out', 'err')
        self.assertEqual(1, len(fixture.procs))
        self.assertEqual(
            dict(
                args=['foo', 'bar'], bufsize=1, executable=None,
                stdin='in', stdout='out', stderr='err',
            ),
            proc._args,
        )

    def test_inject_content_stdout(self):
        def get_info(args):
            return {'stdout': 'stdout'}
        fixture = self.useFixture(FakePopen(get_info))
        proc = fixture(['foo'])
        self.assertEqual('stdout', proc.stdout)

    def test_handles_all_Popen_args(self):
        all_args = dict(
            args="args", bufsize="bufsize", executable="executable",
            stdin="stdin", stdout="stdout", stderr="stderr",
            preexec_fn="preexec_fn", close_fds="close_fds", shell="shell",
            cwd="cwd", env="env", universal_newlines="universal_newlines",
            startupinfo="startupinfo", creationflags="creationflags",
            restore_signals="restore_signals",
            start_new_session="start_new_session", pass_fds="pass_fds",
            encoding="encoding", errors="errors")
        if sys.version_info >= (3, 7):
            all_args["text"] = "text"
        if sys.version_info >= (3, 9):
            all_args["group"] = "group"
            all_args["extra_groups"] = "extra_groups"
            all_args["user"] = "user"
            all_args["umask"] = "umask"
        if sys.version_info >= (3, 10):
            all_args["pipesize"] = "pipesize"
        if sys.version_info >= (3, 11):
            all_args["process_group"] = "process_group"

        def get_info(proc_args):
            self.assertEqual(all_args, proc_args)
            return {}

        fixture = self.useFixture(FakePopen(get_info))
        fixture(**all_args)

    @testtools.skipUnless(
        sys.version_info < (3, 7), "only relevant on Python <3.7")
    def test_rejects_3_7_args_on_older_versions(self):
        fixture = self.useFixture(FakePopen(lambda proc_args: {}))
        with testtools.ExpectedException(
                TypeError, r".* got an unexpected keyword argument 'text'"):
            fixture(args="args", text=True)

    @testtools.skipUnless(
        sys.version_info < (3, 9), "only relevant on Python <3.9")
    def test_rejects_3_9_args_on_older_versions(self):
        fixture = self.useFixture(FakePopen(lambda proc_args: {}))
        for arg_name in ("group", "extra_groups", "user", "umask"):
            kwargs = {arg_name: arg_name}
            expected_message = (
                r".* got an unexpected keyword argument '{}'".format(arg_name))
            with testtools.ExpectedException(TypeError, expected_message):
                fixture(args="args", **kwargs)

    @testtools.skipUnless(
        sys.version_info < (3, 10), "only relevant on Python <3.10")
    def test_rejects_3_10_args_on_older_versions(self):
        fixture = self.useFixture(FakePopen(lambda proc_args: {}))
        with testtools.ExpectedException(
                TypeError,
                r".* got an unexpected keyword argument 'pipesize'"):
            fixture(args="args", pipesize=1024)

    @testtools.skipUnless(
        sys.version_info < (3, 11), "only relevant on Python <3.11")
    def test_rejects_3_11_args_on_older_versions(self):
        fixture = self.useFixture(FakePopen(lambda proc_args: {}))
        with testtools.ExpectedException(
                TypeError,
                r".* got an unexpected keyword argument 'process_group'"):
            fixture(args="args", process_group=42)

    def test_function_signature(self):
        fake_signature = inspect.getfullargspec(FakePopen.__call__)
        real_signature = inspect.getfullargspec(subprocess.Popen)

        # compare args

        fake_args = fake_signature.args
        real_args = real_signature.args

        self.assertListEqual(
            fake_args,
            real_args,
            "Function signature of FakePopen doesn't match subprocess.Popen",
        )

        # compare kw-only args; order doesn't matter so we use a set

        fake_kwargs = set(fake_signature.kwonlyargs)
        real_kwargs = set(real_signature.kwonlyargs)

        if sys.version_info < (3, 11):
            fake_kwargs.remove('process_group')

        if sys.version_info < (3, 10):
            fake_kwargs.remove('pipesize')

        if sys.version_info < (3, 9):
            fake_kwargs.remove('group')
            fake_kwargs.remove('extra_groups')
            fake_kwargs.remove('user')
            fake_kwargs.remove('umask')

        if sys.version_info < (3, 7):
            fake_kwargs.remove('text')

        self.assertSetEqual(
            fake_kwargs,
            real_kwargs,
            "Function signature of FakePopen doesn't match subprocess.Popen",
        )

    def test_custom_returncode(self):
        def get_info(proc_args):
            return dict(returncode=1)
        proc = self.useFixture(FakePopen(get_info))(['foo'])
        self.assertEqual(None, proc.returncode)
        self.assertEqual(1, proc.wait())
        self.assertEqual(1, proc.returncode)

    def test_with_popen_custom(self):
        self.useFixture(FakePopen())
        with subprocess.Popen(['ls -lh']) as proc:
            self.assertEqual(None, proc.returncode)
            self.assertEqual(['ls -lh'], proc.args)


class TestFakeProcess(testtools.TestCase):

    def test_wait(self):
        proc = FakeProcess({}, {})
        proc.returncode = 45
        self.assertEqual(45, proc.wait())

    def test_communicate(self):
        proc = FakeProcess({}, {})
        self.assertEqual(('', ''), proc.communicate())
        self.assertEqual(0, proc.returncode)

    def test_communicate_with_out(self):
        proc = FakeProcess({}, {'stdout': io.BytesIO(b'foo')})
        self.assertEqual((b'foo', ''), proc.communicate())
        self.assertEqual(0, proc.returncode)

    def test_communicate_with_input(self):
        proc = FakeProcess({}, {'stdout': io.BytesIO(b'foo')})
        self.assertEqual((b'foo', ''), proc.communicate(input=b'bar'))

    def test_communicate_with_input_and_stdin(self):
        stdin = io.BytesIO()
        proc = FakeProcess({}, {'stdin': stdin})
        proc.communicate(input=b'hello')
        self.assertEqual(b'hello', stdin.getvalue())

    def test_communicate_with_timeout(self):
        proc = FakeProcess({}, {'stdout': io.BytesIO(b'foo')})
        self.assertEqual((b'foo', ''), proc.communicate(timeout=10))

    def test_args(self):
        proc = FakeProcess({"args": ["ls", "-lh"]}, {})
        proc.returncode = 45
        self.assertEqual(45, proc.wait())
        self.assertEqual(proc.args, ["ls", "-lh"])

    def test_kill(self):
        proc = FakeProcess({}, {})
        self.assertIs(None, proc.kill())

    def test_poll(self):
        proc = FakeProcess({}, {})
        self.assertIs(None, proc.poll())
        proc.communicate()
        self.assertEqual(0, proc.poll())

    def test_poll_with_returncode(self):
        proc = FakeProcess({}, {})
        proc.communicate()
        self.assertEqual(0, proc.poll())

    def test_wait_with_timeout_and_endtime(self):
        proc = FakeProcess({}, {})
        self.assertEqual(0, proc.wait(timeout=4, endtime=7))
