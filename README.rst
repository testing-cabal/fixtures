************************************************************
fixtures: Fixtures with cleanups for testing and convenience
************************************************************

*fixtures* defines a Python contract for reusable state / support logic,
primarily for unit testing. Helper and adaption logic is included to make it
easy to write your own fixtures using the fixtures contract. Glue code is
provided that makes using fixtures that meet the ``Fixtures`` contract in
``unittest`` compatible test cases easy and straight forward.

Dependencies
============

* Python 3.8+
  This is the base language fixtures is written in and for.

The ``fixtures[streams]`` extra adds:

* ``testtools`` <https://launchpad.net/testtools>

  ``testtools`` provides helpful glue functions for the details API used to report
  information about a fixture (whether its used in a testing or production
  environment).

For use in a unit test suite using the included glue, you will need a test
environment that supports ``TestCase.addCleanup``. Writing your own glue code
is easy. Alternatively, you can simply use Fixtures directly without any
support code.

To run the test suite for fixtures, ``testtools`` is needed.

Why Fixtures
============

Standard Python ``unittest`` provides no obvious method for making and reusing
state needed in a test case other than by adding a method on the test class.
This scales poorly - complex helper functions propagating up a test class
hierarchy is a regular pattern when this is done. Mocking, while a great tool,
doesn't itself prevent this (and helpers to mock complex things can accumulate
in the same way if placed on the test class).

By defining a uniform contract where helpers have no dependency on the test
class we permit all the regular code hygiene activities to take place without
the distorting influence of being in a class hierarchy that is modelling an
entirely different thing - which is what helpers on a ``TestCase`` suffer from.

About Fixtures
==============

A fixture represents some state. Each fixture has attributes on it that are
specific to the fixture. For instance, a fixture representing a directory that
can be used for temporary files might have a attribute ``path``.

Most fixtures have complete ``pydoc`` documentation, so be sure to check
``pydoc fixtures`` for usage information.

Creating Fixtures
=================

Minimally, subclass ``Fixture``, define ``_setUp`` to initialize your state,
schedule a cleanup for when ``cleanUp`` is called, and you're done:

.. code-block:: python

  >>> import unittest
  >>> import fixtures
  >>> class NoddyFixture(fixtures.Fixture):
  ...     def _setUp(self):
  ...         self.frobnozzle = 42
  ...         self.addCleanup(delattr, self, 'frobnozzle')

This will initialize ``frobnozzle`` when ``setUp`` is called, and when
``cleanUp`` is called get rid of the ``frobnozzle`` attribute. Prior to version
1.3.0 *fixtures* recommended overriding ``setUp``. This is still supported, but
since it is harder to write leak-free fixtures in this fashion, it is not
recommended.

If your fixture has diagnostic data - for instance the log file of an
application server, or log messages - it can expose that by creating a content
object (``testtools.content.Content``) and calling ``addDetail``:

.. code-block:: python

  >>> from testtools.content import text_content
  >>> class WithLog(fixtures.Fixture):
  ...     def _setUp(self):
  ...         self.addDetail('message', text_content('foo bar baz'))

The method ``useFixture`` will use another fixture, call ``setUp`` on it, call
``self.addCleanup(thefixture.cleanUp)``, attach any details from it and return
the fixture. This allows simple composition of different fixtures:

.. code-block:: python

  >>> class ReusingFixture(fixtures.Fixture):
  ...     def _setUp(self):
  ...         self.noddy = self.useFixture(NoddyFixture())

There is a helper for adapting a function or function pair into Fixtures. It
puts the result of the function in ``fn_result``:

.. code-block:: python

  >>> import os.path
  >>> import shutil
  >>> import tempfile
  >>> def setup_function():
  ...     return tempfile.mkdtemp()
  >>> def teardown_function(fixture):
  ...     shutil.rmtree(fixture)
  >>> fixture = fixtures.FunctionFixture(setup_function, teardown_function)
  >>> fixture.setUp()
  >>> print (os.path.isdir(fixture.fn_result))
  True
  >>> fixture.cleanUp()

This can be expressed even more pithily:

.. code-block:: python

  >>> fixture = fixtures.FunctionFixture(tempfile.mkdtemp, shutil.rmtree)
  >>> fixture.setUp()
  >>> print (os.path.isdir(fixture.fn_result))
  True
  >>> fixture.cleanUp()

Another variation is ``MethodFixture`` which is useful for adapting alternate
fixture implementations to Fixture:

.. code-block:: python

  >>> class MyServer:
  ...    def start(self):
  ...        pass
  ...    def stop(self):
  ...        pass
  >>> server = MyServer()
  >>> fixture = fixtures.MethodFixture(server, server.start, server.stop)

You can also combine existing fixtures using ``CompoundFixture``:

.. code-block:: python

  >>> noddy_with_log = fixtures.CompoundFixture([NoddyFixture(),
  ...                                            WithLog()])
  >>> with noddy_with_log as x:
  ...     print (x.fixtures[0].frobnozzle)
  42

The Fixture API
===============

The example above introduces some of the ``Fixture`` API. In order to be able
to clean up after a fixture has been used, all fixtures define a ``cleanUp``
method which should be called when a fixture is finished with.

Because it's nice to be able to build a particular set of related fixtures in
advance of using them, fixtures also have a ``setUp`` method which should be
called before trying to use them.

One common desire with fixtures that are expensive to create is to reuse them
in many test cases; to support this the base ``Fixture`` also defines a
``reset`` which calls ``self.cleanUp(); self.setUp()``. Fixtures that can more
efficiently make themselves reusable should override this method. This can then
be used with multiple test state via things like ``testresources``,
``setUpClass``, or ``setUpModule``.

When using a fixture with a test you can manually call the ``setUp`` and
``cleanUp`` methods. More convenient though is to use the included glue from
``fixtures.TestWithFixtures`` which provides a mixin defining ``useFixture``
(camel case because ``unittest`` is camel case throughout) method. It will call
``setUp`` on the fixture, call ``self.addCleanup(fixture)`` to schedule a
cleanup, and return the fixture. This lets one write:

.. code-block:: python

  >>> import testtools
  >>> import unittest

Note that we use ``testtools.TestCase``. ``testtools`` has it's own
implementation of ``useFixture`` so there is no need to use
``fixtures.TestWithFixtures`` with ``testtools.TestCase``:

.. code-block:: python

  >>> class NoddyTest(testtools.TestCase, fixtures.TestWithFixtures):
  ...     def test_example(self):
  ...         fixture = self.useFixture(NoddyFixture())
  ...         self.assertEqual(42, fixture.frobnozzle)
  >>> result = unittest.TestResult()
  >>> _ = NoddyTest('test_example').run(result)
  >>> print (result.wasSuccessful())
  True

Fixtures implement the context protocol, so you can also use a fixture as a
context manager:

.. code-block:: python

  >>> with fixtures.FunctionFixture(setup_function, teardown_function) as fixture:
  ...    print (os.path.isdir(fixture.fn_result))
  True

When multiple cleanups error, ``fixture.cleanUp()`` will raise a wrapper
exception rather than choosing an arbitrary single exception to raise:

.. code-block:: python

  >>> import sys
  >>> from fixtures.fixture import MultipleExceptions
  >>> class BrokenFixture(fixtures.Fixture):
  ...     def _setUp(self):
  ...         self.addCleanup(lambda:1/0)
  ...         self.addCleanup(lambda:1/0)
  >>> fixture = BrokenFixture()
  >>> fixture.setUp()
  >>> try:
  ...    fixture.cleanUp()
  ... except MultipleExceptions:
  ...    exc_info = sys.exc_info()
  >>> print (exc_info[1].args[0][0].__name__)
  ZeroDivisionError

Fixtures often expose diagnostic details that can be useful for tracking down
issues. The ``getDetails`` method will return a dict of all the attached
details but can only be called before ``cleanUp`` is called. Each detail
object is an instance of ``testtools.content.Content``:

.. code-block:: python

  >>> with WithLog() as l:
  ...     print(l.getDetails()['message'].as_text())
  foo bar baz

Errors in setUp
+++++++++++++++

The examples above used ``_setUp`` rather than ``setUp`` because the base
class implementation of ``setUp`` acts to reduce the chance of leaking
external resources if an error is raised from ``_setUp``. Specifically,
``setUp`` contains a try/except block which catches all exceptions, captures
any registered detail objects, and calls ``self.cleanUp`` before propagating
the error. As long as you take care to register any cleanups before calling
the code that may fail, this will cause them to be cleaned up. The captured
detail objects are provided to the args of the raised exception.

If the error that occurred was a subclass of ``Exception`` then ``setUp`` will
raise ``MultipleExceptions`` with the last element being a ``SetupError`` that
contains the detail objects. Otherwise, to prevent causing normally
uncatchable errors like ``KeyboardInterrupt`` being caught inappropriately in
the calling layer, the original exception will be raised as-is and no
diagnostic data other than that from the original exception will be available.

Shared Dependencies
+++++++++++++++++++

A common use case within complex environments is having some fixtures shared by
other ones.

Consider the case of testing using a ``TempDir`` with two fixtures built on top
of it; say a small database and a web server. Writing either one is nearly
trivial. However handling ``reset()`` correctly is hard: both the database and
web server would reasonably expect to be able to discard operating system
resources they may have open within the temporary directory before its removed.
A recursive ``reset()`` implementation would work for one, but not both.
Calling ``reset()`` on the ``TempDir`` instance between each test is probably
desirable but we don't want to have to do a complete ``cleanUp`` of the higher
layer fixtures (which would make the ``TempDir`` be unused and trivially
resettable. We have a few options available to us.

Imagine that the webserver does not depend on the DB fixture in any way - we
just want the webserver and DB fixture to coexist in the same tempdir.

A simple option is to just provide an explicit dependency fixture for the
higher layer fixtures to use.  This pushes complexity out of the core and onto
users of fixtures:

.. code-block:: python

  >>> class WithDep(fixtures.Fixture):
  ...     def __init__(self, tempdir, dependency_fixture):
  ...         super(WithDep, self).__init__()
  ...         self.tempdir = tempdir
  ...         self.dependency_fixture = dependency_fixture
  ...     def setUp(self):
  ...         super(WithDep, self).setUp()
  ...         self.addCleanup(self.dependency_fixture.cleanUp)
  ...         self.dependency_fixture.setUp()
  ...         # we assume that at this point self.tempdir is usable.
  >>> DB = WithDep
  >>> WebServer = WithDep
  >>> tempdir = fixtures.TempDir()
  >>> db = DB(tempdir, tempdir)
  >>> server = WebServer(tempdir, db)
  >>> server.setUp()
  >>> server.cleanUp()

Another option is to write the fixtures to gracefully handle a dependency
being reset underneath them. This is insufficient if the fixtures would
block the dependency resetting (for instance by holding file locks open
in a tempdir - on Windows this will prevent the directory being deleted).

Another approach which ``fixtures`` neither helps nor hinders is to raise
a signal of some sort for each user of a fixture before it is reset. In the
example here, ``TempDir`` might offer a subscribers attribute that both the
DB and web server would be registered in. Calling ``reset`` or ``cleanUp``
on the tempdir would trigger a callback to all the subscribers; the DB and
web server reset methods would look something like:

.. code-block:: python

  >>> def reset(self):
  ...     if not self._cleaned:
  ...         self._clean()

(Their action on the callback from the tempdir would be to do whatever work
was needed and set ``self._cleaned``.) This approach has the (perhaps)
surprising effect that resetting the webserver may reset the DB - if the
webserver were to be depending on ``tempdir.reset`` as a way to reset the
webserver's state.

Another approach which is not currently implemented is to provide an object
graph of dependencies and a reset mechanism that can traverse that, along with
a separation between 'reset starting' and 'reset finishing' - the DB and
webserver would both have their ``reset_starting`` methods called, then the
tempdir would be reset, and finally the DB and webserver would have
``reset_finishing`` called.

Stock Fixtures
==============

In addition to the ``Fixture``, ``FunctionFixture`` and ``MethodFixture``
classes, fixtures includes a number of pre-canned fixtures. The API docs for
fixtures will list the complete set of these, should the docs be out of date or
not to hand. For the complete feature set of each fixture please see the API
docs.

``ByteStream``
++++++++++++++

Trivial adapter to make a ``BytesIO`` (though it may in future auto-spill to
disk for large content) and expose that as a detail object, for automatic
inclusion in test failure descriptions. Very useful in combination with
``MonkeyPatch``:

.. code-block:: python

  >>> fixture = fixtures.StringStream('my-content')
  >>> fixture.setUp()
  >>> with fixtures.MonkeyPatch('sys.something', fixture.stream):
  ...     pass
  >>> fixture.cleanUp()

This requires the ``fixtures[streams]`` extra.

``EnvironmentVariable``
+++++++++++++++++++++++

Isolate your code from environmental variables, delete them or set them to a
new value:

.. code-block:: python

  >>> fixture = fixtures.EnvironmentVariable('HOME')

``FakeLogger``
++++++++++++++

Isolate your code from an external logging configuration - so that your test
gets the output from logged messages, but they don't go to e.g. the console:

.. code-block:: python

  >>> fixture = fixtures.FakeLogger()

``FakePopen``
+++++++++++++

Pretend to run an external command rather than needing it to be present to run
tests:

.. code-block:: python

  >>> from io import BytesIO
  >>> fixture = fixtures.FakePopen(lambda _:{'stdout': BytesIO('foobar')})

``LogHandler``
++++++++++++++

Replace or extend a logger's handlers. The behavior of this fixture depends on
the value of the ``nuke_handlers`` parameter: if ``true``, the logger's
existing handlers are removed and replaced by the provided handler, while if
``false`` the logger's set of handlers is extended by the provided handler:

.. code-block:: python

  >>> from logging import StreamHandler
  >>> fixture = fixtures.LogHandler(StreamHandler())

``MockPatchObject``
+++++++++++++++++++

Adapts ``unittest.mock.patch.object`` to be used as a fixture:

.. code-block:: python

  >>> class Fred:
  ...     value = 1
  >>> fixture = fixtures.MockPatchObject(Fred, 'value', 2)
  >>> with fixture:
  ...     Fred().value
  2
  >>> Fred().value
  1

``MockPatch``
+++++++++++++

Adapts ``unittest.mock.patch`` to be used as a fixture:

.. code-block:: python

  >>> fixture = fixtures.MockPatch('subprocess.Popen.returncode', 3)

``MockPatchMultiple``
+++++++++++++++++++++

Adapts ``unittest.mock.patch.multiple`` to be used as a ``fixture``:

.. code-block:: python

  >>> fixture = fixtures.MockPatchMultiple('subprocess.Popen', returncode=3)

``MonkeyPatch``
+++++++++++++++

Control the value of a named Python attribute

.. code-block:: python

  >>> def fake_open(path, mode):
  ...     pass
  >>> fixture = fixtures.MonkeyPatch('__builtin__.open', fake_open)

Note that there are some complexities when patching methods - please see the
API documentation for details.

``NestedTempfile``
++++++++++++++++++

Change the default directory that the ``tempfile`` module places temporary
files and directories in. This can be useful for containing the noise created
by code which doesn't clean up its temporary files. This does not affect
temporary file creation where an explicit containing directory was provided

.. code-block:: python

  >>> fixture = fixtures.NestedTempfile()

``PackagePathEntry``
++++++++++++++++++++

Adds a single directory to the path for an existing Python package. This adds
to the ``package.__path__`` list. If the directory is already in the path,
nothing happens, if it isn't then it is added on ``setUp`` and removed on
``cleanUp``:

.. code-block:: python

  >>> fixture = fixtures.PackagePathEntry('package/name', '/foo/bar')

``PythonPackage``
+++++++++++++++++

Creates a python package directory. Particularly useful for testing code that
dynamically loads packages/modules, or for mocking out the command line entry
points to Python programs:

.. code-block:: python

  >>> fixture = fixtures.PythonPackage('foo.bar', [('quux.py', '')])

``PythonPathEntry``
+++++++++++++++++++

Adds a single directory to ``sys.path``. If the directory is already in the
path, nothing happens, if it isn't then it is added on ``setUp`` and removed on
``cleanUp``:

.. code-block:: python

  >>> fixture = fixtures.PythonPathEntry('/foo/bar')

``Stream``
++++++++++

Trivial adapter to expose a file-like object as a detail object, for automatic
inclusion in test failure descriptions. ``StringStream`` and ``BytesStream``
provided concrete users of this fixture.

This requires the ``fixtures[streams]`` extra.

``StringStream``
++++++++++++++++

Trivial adapter to make a ``StringIO`` (though it may in future auto-spill to
disk for large content) and expose that as a detail object, for automatic
inclusion in test failure descriptions. Very useful in combination with
``MonkeyPatch``:

.. code-block:: python

  >>> fixture = fixtures.StringStream('stdout')
  >>> fixture.setUp()
  >>> with fixtures.MonkeyPatch('sys.stdout', fixture.stream):
  ...     pass
  >>> fixture.cleanUp()

This requires the ``fixtures[streams]`` extra.

``TempDir``
+++++++++++

Create a temporary directory and clean it up later:

.. code-block:: python

  >>> fixture = fixtures.TempDir()

The created directory is stored in the ``path`` attribute of the fixture after
``setUp``.

``TempHomeDir``
+++++++++++++++

Create a temporary directory and set it as ``$HOME`` in the environment:

.. code-block:: python

  >>> fixture = fixtures.TempHomeDir()

The created directory is stored in the ``path`` attribute of the fixture after
``setUp``.

The environment will now have ``$HOME`` set to the same path, and the value
will be returned to its previous value after ``tearDown``.

``Timeout``
+++++++++++

Aborts if the covered code takes more than a specified number of whole wall-clock
seconds.

There are two possibilities, controlled by the ``gentle`` argument: when gentle,
an exception will be raised and the test (or other covered code) will fail.
When not gentle, the entire process will be terminated, which is less clean,
but more likely to break hangs where no Python code is running.

.. caution::

   Only one timeout can be active at any time across all threads in a single
   process.  Using more than one has undefined results.  (This could be improved
   by chaining alarms.)

.. note::

   Currently supported only on Unix because it relies on the ``alarm`` system
   call.

``WarningsCapture``
+++++++++++++++++++

Capture warnings for later analysis:

.. code-block:: python

  >>> fixture = fixtures.WarningsCapture()

The captured warnings are stored in the ``captures`` attribute of the fixture
after ``setUp``.

``WarningsFilter``
++++++++++++++++++

Configure warnings filters during test runs:

.. code-block:: python

  >>> fixture = fixtures.WarningsFilter(
  ...     [
  ...         {
  ...             'action': 'ignore',
  ...             'message': 'foo',
  ...             'category': DeprecationWarning,
  ...         },
  ...     ]
  ... )

Order is important: entries closer to the front of the list override entries
later in the list, if both match a particular warning.

Contributing
============

Fixtures has its project homepage on GitHub
<https://github.com/testing-cabal/fixtures>.

License
=======

  Copyright (c) 2010, Robert Collins <robertc@robertcollins.net>

  Licensed under either the Apache License, Version 2.0 or the BSD 3-clause
  license at the users choice. A copy of both licenses are available in the
  project source as Apache-2.0 and BSD. You may not use this file except in
  compliance with one of these two licences.

  Unless required by applicable law or agreed to in writing, software
  distributed under these licenses is distributed on an "AS IS" BASIS, WITHOUT
  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
  license you chose for the specific language governing permissions and
  limitations under that license.
