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
    'Fixture',
    'FunctionFixture',
    ]


class Fixture(object):
    """A Fixture representing some state or resource.

    Often used in tests, a Fixture must be setUp before using it, and cleanUp
    called after it is finished with (because many Fixture classes have
    external resources such as temporary directories).

    The reset() method can be called to perform cleanUp and setUp automatically
    and potentially faster.
    """

    def addCleanup(self, cleanup, *args, **kwargs):
        """Add a clean function to be called from cleanUp.

        All cleanup functions are called and regular exceptions caught and
        swallowed.

        If for some reason you need to cancel cleanups, call
        self._clear_cleanups.

        :param cleanup: A callable to call during cleanUp.
        :param *args: Positional args for cleanup.
        :param kwargs: Keyword args for cleanup.
        :return: None
        """
        self._cleanups.append((cleanup, args, kwargs))

    def cleanUp(self):
        """Cleanup the fixture.

        This function will free all resources managed by the Fixture, restoring
        it (and any external facilities such as databases, temporary
        directories and so forth_ to their original state.

        This should not typically be overridden, see addCleanup instead.
        """
        cleanups = reversed(self._cleanups)
        self._clear_cleanups()
        for cleanup, args, kwargs in cleanups:
            try:
                cleanup(*args, **kwargs)
            except Exception:
                # For now, swallow exceptions.
                pass

    def _clear_cleanups(self):
        """Clean the cleanup queue without running them.

        This is a helper that can be useful for subclasses which define
        reset(): they may perform something equivalent to a typical cleanUp
        without actually calling the cleanups.
        """
        self._cleanups = []

    def __enter__(self):
        self.setUp()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanUp()
        return False # propogate exceptions from the with body.

    def setUp(self):
        """Prepare the Fixture for use.

        This should be overridden by most concrete fixtures. When overriding
        be sure to include self.addCleanup calls to restore the fixture to 
        an un-setUp state, so that a single Fixture instance can be reused.

        After setUp is called, the fixture will have one or more attributes
        which can be used (these depend totally on the concrete subclass).

        :return: None.
        """
        self._clear_cleanups()


    def reset(self):
        """Reset a setUp Fixture to the 'just setUp' state again.

        The default implementation calls
        self.cleanUp()
        self.setUp()

        but this function may be overridden to provide an optimised routine to
        achieve the same result.

        :return: None.
        """
        self.cleanUp()
        self.setUp()


class FunctionFixture(Fixture):
    """An adapter to use function(s) as a Fixture.

    Typically used when an existing object or function interface exists but you
    wish to use it as a Fixture (e.g. because fixtures are in use in your test
    suite and this will fit in better).

    To adapt an object with differently named setUp and cleanUp methods:
    fixture = FunctionFixture(object.install, object.__class__.remove)

    To adapt functions:
    fixture = FunctionFixture(tempfile.mkdtemp, shutil.rmtree)

    With a reset function:
    fixture = FunctionFixture(setup, cleanup, reset)

    :ivar fn_result: The result of the setup_fn. Undefined outside of the
        setUp, cleanUp context.
    """

    def __init__(self, setup_fn, cleanup_fn=None, reset_fn=None):
        """Create a FunctionFixture.

        :param setup_fn: A callable which takes no parameters and returns the
            thing you want to use. e.g.
            def setup_fn():
                return 42
            The result of setup_fn is assigned to the fn_result attribute bu
            FunctionFixture.setUp.
        :param cleanup_fn: Optional callable which takes a single parameter, which
            must be that which is returned from the setup_fn. This is called
            from cleanUp.
        :param reset_fn: Optional callable which takes a single parameter like
            cleanup_fn, but also returns a new object for use as the fn_result:
            if defined this replaces the use of cleanup_fn and setup_fn when
            reset() is called.
        """
        self.setup_fn = setup_fn
        self.cleanup_fn = cleanup_fn
        self.reset_fn = reset_fn

    def setUp(self):
        super(FunctionFixture, self).setUp()
        fn_result = self.setup_fn()
        self._maybe_cleanup(fn_result)

    def reset(self):
        if self.reset_fn is None:
            super(FunctionFixture, self).reset()
        else:
            self._clear_cleanups()
            fn_result = self.reset_fn(self.fn_result)
            self._maybe_cleanup(fn_result)

    def _maybe_cleanup(self, fn_result):
        self.addCleanup(delattr, self, 'fn_result')
        if self.cleanup_fn is not None:
            self.addCleanup(self.cleanup_fn, fn_result)
        self.fn_result = fn_result
