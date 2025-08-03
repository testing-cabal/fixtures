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
    "FakePopen",
    "PopenFixture",
]

import random
import subprocess
import sys
from typing import Any, Callable, Dict, IO, List, Optional, Tuple, Union, Final

from fixtures import Fixture


class _Unpassed:
    """Sentinel type for unpassed arguments."""

    pass


_unpassed: Final = _Unpassed()


class FakeProcess(object):
    """A test double process, roughly meeting subprocess.Popen's contract."""

    def __init__(self, args: Dict[str, Any], info: Dict[str, Any]) -> None:
        self._args = args
        self.stdin: Any = info.get("stdin")
        self.stdout: Any = info.get("stdout")
        self.stderr: Any = info.get("stderr")
        self.pid: int = random.randint(0, 65536)
        self._returncode: int = info.get("returncode", 0)
        self.returncode: Optional[int] = None

    @property
    def args(self) -> Any:
        return self._args["args"]

    def poll(self) -> Optional[int]:
        """Get the current value of FakeProcess.returncode.

        The returncode is None before communicate() and/or wait() are called,
        and it's set to the value provided by the 'info' dictionary otherwise
        (or 0 in case 'info' doesn't specify a value).
        """
        return self.returncode

    def communicate(
        self, input: Optional[Union[bytes, str]] = None, timeout: Optional[float] = None
    ) -> Tuple[Any, Any]:
        self.returncode = self._returncode
        if self.stdin and input:
            self.stdin.write(input)
        if self.stdout:
            out = self.stdout.getvalue()
        else:
            out = ""
        if self.stderr:
            err = self.stderr.getvalue()
        else:
            err = ""
        return out, err

    def __enter__(self) -> "FakeProcess":
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.wait()

    def kill(self) -> None:
        pass

    def wait(
        self, timeout: Optional[float] = None, endtime: Optional[float] = None
    ) -> Optional[int]:
        if self.returncode is None:
            self.communicate()
        return self.returncode


class FakePopen(Fixture):
    """Replace subprocess.Popen.

    Primarily useful for testing, this fixture replaces subprocess.Popen with a
    test double.

    :ivar procs: A list of the processes created by the fixture.
    """

    def __init__(
        self, get_info: Callable[[Dict[str, Any]], Dict[str, Any]] = lambda _: {}
    ) -> None:
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

            After communicate() or wait() are called on the process object,
            the returncode is set to whatever get_info returns (or 0 if
            get_info is not supplied or doesn't return a dict with an explicit
            'returncode' key).
        """
        super(FakePopen, self).__init__()
        self.get_info = get_info

    def _setUp(self) -> None:
        self.addCleanup(setattr, subprocess, "Popen", subprocess.Popen)
        subprocess.Popen = self  # type: ignore[assignment,misc]
        self.procs: List[FakeProcess] = []

    # The method has the correct signature so we error appropriately if called
    # wrongly.
    def __call__(
        self,
        args: Union[str, List[str]],
        bufsize: Union[int, _Unpassed] = _unpassed,
        executable: Union[str, None, _Unpassed] = _unpassed,
        stdin: Union[None, int, IO[Any], _Unpassed] = _unpassed,
        stdout: Union[None, int, IO[Any], _Unpassed] = _unpassed,
        stderr: Union[None, int, IO[Any], _Unpassed] = _unpassed,
        preexec_fn: Union[Callable[[], None], None, _Unpassed] = _unpassed,
        close_fds: Union[bool, _Unpassed] = _unpassed,
        shell: Union[bool, _Unpassed] = _unpassed,
        cwd: Union[str, None, _Unpassed] = _unpassed,
        env: Union[Dict[str, str], None, _Unpassed] = _unpassed,
        universal_newlines: Union[bool, _Unpassed] = _unpassed,
        startupinfo: Union[Any, _Unpassed] = _unpassed,
        creationflags: Union[int, _Unpassed] = _unpassed,
        restore_signals: Union[bool, _Unpassed] = _unpassed,
        start_new_session: Union[bool, _Unpassed] = _unpassed,
        pass_fds: Union[Any, _Unpassed] = _unpassed,
        *,
        group: Union[str, int, None, _Unpassed] = _unpassed,
        extra_groups: Union[List[Union[str, int]], None, _Unpassed] = _unpassed,
        user: Union[str, int, None, _Unpassed] = _unpassed,
        umask: Union[int, None, _Unpassed] = _unpassed,
        encoding: Union[str, None, _Unpassed] = _unpassed,
        errors: Union[str, None, _Unpassed] = _unpassed,
        text: Union[bool, None, _Unpassed] = _unpassed,
        pipesize: Union[int, _Unpassed] = _unpassed,
        process_group: Union[int, None, _Unpassed] = _unpassed,
    ) -> FakeProcess:
        if sys.version_info < (3, 9):
            for arg_name in "group", "extra_groups", "user", "umask":
                if not isinstance(locals()[arg_name], _Unpassed):
                    raise TypeError(
                        "FakePopen.__call__() got an unexpected keyword "
                        "argument '{}'".format(arg_name)
                    )
        if sys.version_info < (3, 10) and not isinstance(pipesize, _Unpassed):
            raise TypeError(
                "FakePopen.__call__() got an unexpected keyword argument 'pipesize'"
            )
        if sys.version_info < (3, 11) and not isinstance(process_group, _Unpassed):
            raise TypeError(
                "FakePopen.__call__() got an unexpected keyword argument "
                "'process_group'"
            )

        proc_args = dict(args=args)
        local = locals()
        for param in [
            "bufsize",
            "executable",
            "stdin",
            "stdout",
            "stderr",
            "preexec_fn",
            "close_fds",
            "shell",
            "cwd",
            "env",
            "universal_newlines",
            "startupinfo",
            "creationflags",
            "restore_signals",
            "start_new_session",
            "pass_fds",
            "group",
            "extra_groups",
            "user",
            "umask",
            "encoding",
            "errors",
            "text",
            "pipesize",
            "process_group",
        ]:
            if not isinstance(local[param], _Unpassed):
                proc_args[param] = local[param]
        proc_info = self.get_info(proc_args)
        result = FakeProcess(proc_args, proc_info)
        self.procs.append(result)
        return result


PopenFixture = FakePopen
