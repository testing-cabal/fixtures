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
    'CompoundFixture',
    'Fixture',
    'FunctionFixture',
    'MethodFixture',
    'MultipleExceptions',
    'SetupError',
    ]

import itertools
import sys

import six
from testtools.compat import (
    advance_iterator,
    )
from testtools.helpers import try_import

from fixtures.callmany import (
    CallMany,
    # Deprecated, imported for compatibility.
    MultipleExceptions,
    )

gather_details = try_import("testtools.testcase.gather_details")

# This would be better in testtools (or a common library)
def combine_details(source_details, target_details):
    """Add every value from source to target deduping common keys."""
    for name, content_object in source_details.items():
        new_name = name
        disambiguator = itertools.count(1)
        while new_name in target_details:
            new_name = '%s-%d' % (name, advance_iterator(disambiguator))
        name = new_name
        target_details[name] = content_object


class SetupError(Exception):
    """Setup failed.

    args[0] will be a details dict.
    """


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

        All cleanup functions are called - see cleanUp for details on how
        multiple exceptions are handled.

        If for some reason you need to cancel cleanups, call
        self._clear_cleanups.

        :param cleanup: A callable to call during cleanUp.
        :param *args: Positional args for cleanup.
        :param kwargs: Keyword args for cleanup.
        :return: None
        """
        self._cleanups.push(cleanup, *args, **kwargs)

    def addDetail(self, name, content_object):
        """Add a detail to the Fixture.

        This may only be called after setUp has been called.

        :param name: The name for the detail being added. Overrides existing
            identically named details.
        :param content_object: The content object (meeting the
            testtools.content.Content protocol) being added.
        """
        self._details[name] = content_object

    def cleanUp(self, raise_first=True):
        """Cleanup the fixture.

        This function will free all resources managed by the Fixture, restoring
        it (and any external facilities such as databases, temporary
        directories and so forth_ to their original state.

        This should not typically be overridden, see addCleanup instead.

        cleanUp may be called once and only once after setUp() has been called.
        The base implementation of setUp will automatically call cleanUp if
        an exception occurs within setUp itself.

        :param raise_first: Deprecated parameter from before testtools gained
            MultipleExceptions. raise_first defaults to True. When True
            if a single exception is raised, it is reraised after all the
            cleanUps have run. If multiple exceptions are raised, they are
            all wrapped into a MultipleExceptions object, and that is reraised.
            Thus, to catch a specific exception from cleanUp, you need to catch
            both the exception and MultipleExceptions, and then check within
            a MultipleExceptions instance for the type you're catching.
        :return: A list of the exc_info() for each exception that occured if
            raise_first was False
        """
        try:
            return self._cleanups(raise_errors=raise_first)
        finally:
            self._remove_state()

    def _clear_cleanups(self):
        """Clean the cleanup queue without running them.

        This is a helper that can be useful for subclasses which define
        reset(): they may perform something equivalent to a typical cleanUp
        without actually calling the cleanups.

        This also clears the details dict.
        """
        self._cleanups = CallMany()
        self._details = {}
        self._detail_sources = []

    def _remove_state(self):
        """Remove the internal state.

        Called from cleanUp to put the fixture back into a not-ready state.
        """
        self._cleanups = None
        self._details = None
        self._detail_sources = None

    def __enter__(self):
        self.setUp()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self._cleanups()
        finally:
            self._remove_state()
        return False  # propagate exceptions from the with body.

    def getDetails(self):
        """Get the current details registered with the fixture.

        This does not return the internal dictionary: mutating it will have no
        effect. If you need to mutate it, just do so directly.

        :return: Dict from name -> content_object.
        """
        result = dict(self._details)
        for source in self._detail_sources:
            combine_details(source.getDetails(), result)
        return result

    def setUp(self):
        """Prepare the Fixture for use.

        This should not be overridden. Concrete fixtures should implement
        _setUp. Overriding of setUp is still supported, just not recommended.

        After setUp has completed, the fixture will have one or more attributes
        which can be used (these depend totally on the concrete subclass).

        :raises: MultipleExceptions if _setUp fails. The last exception
            captured within the MultipleExceptions will be a SetupError
            exception.
        :return: None.

        :changed in 1.3: The recommendation to override setUp has been
            reversed - before 1.3, setUp() should be overridden, now it should
            not be.
        :changed in 1.3.1: BaseException is now caught, and only subclasses of
            Exception are wrapped in MultipleExceptions.
        """
        self._clear_cleanups()
        try:
            self._setUp()
        except:
            err = sys.exc_info()
            details = {}
            if gather_details is not None:
                # Materialise all details since we're about to cleanup.
                gather_details(self.getDetails(), details)
            else:
                details = self.getDetails()
            errors = [err] + self.cleanUp(raise_first=False)
            try:
                raise SetupError(details)
            except SetupError:
                errors.append(sys.exc_info())
            if issubclass(err[0], Exception):
                raise MultipleExceptions(*errors)
            else:
                six.reraise(*err)

    def _setUp(self):
        """Template method for subclasses to override.

        Override this to customise the fixture. When overriding
        be sure to include self.addCleanup calls to restore the fixture to
        an un-setUp state, so that a single Fixture instance can be reused.

        Fixtures will never have a body in _setUp - calling super() is
        entirely at the discretion of subclasses.

        :return: None.
        """

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

    def useFixture(self, fixture):
        """Use another fixture.

        The fixture will be setUp, and self.addCleanup(fixture.cleanUp) called.
        If the fixture fails to set up, useFixture will attempt to gather its
        details into this fixture's details to aid in debugging.

        :param fixture: The fixture to use.
        :return: The fixture, after setting it up and scheduling a cleanup for
           it.
        :raises: Any errors raised by the fixture's setUp method.
        """
        try:
            fixture.setUp()
        except MultipleExceptions as e:
            if e.args[-1][0] is SetupError:
                combine_details(e.args[-1][1].args[0], self._details)
            raise
        except:
            # The child failed to come up and didn't raise MultipleExceptions
            # which we can understand... capture any details it has (copying
            # the content, it may go away anytime).
            if gather_details is not None:
                gather_details(fixture.getDetails(), self._details)
            raise
        else:
            self.addCleanup(fixture.cleanUp)
            # Calls to getDetails while this fixture is setup will return
            # details from the child fixture.
            self._detail_sources.append(fixture)
            return fixture


class FunctionFixture(Fixture):
    """An adapter to use function(s) as a Fixture.

    Typically used when an existing object or function interface exists but you
    wish to use it as a Fixture (e.g. because fixtures are in use in your test
    suite and this will fit in better).

    To adapt an object with differently named setUp and cleanUp methods:
    fixture = FunctionFixture(object.install, object.__class__.remove)
    Note that the indirection via __class__ is to get an unbound method
    which can accept the result from install. See also MethodFixture which
    is specialised for objects.

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
        super(FunctionFixture, self).__init__()
        self.setup_fn = setup_fn
        self.cleanup_fn = cleanup_fn
        self.reset_fn = reset_fn

    def _setUp(self):
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


class MethodFixture(Fixture):
    """An adapter to use a function as a Fixture.

    Typically used when an existing object exists but you wish to use it as a
    Fixture (e.g. because fixtures are in use in your test suite and this will
    fit in better).

    To adapt an object with setUp / tearDown methods:
    fixture = MethodFixture(object)
    If setUp / tearDown / reset are missing, they simply won't be called.

    The object is exposed on fixture.obj.

    To adapt an object with differently named setUp and cleanUp methods:
    fixture = MethodFixture(object, setup=object.mySetUp,
        teardown=object.myTearDown)

    With a differently named reset function:
    fixture = MethodFixture(object, reset=object.myReset)

    :ivar obj: The object which is being wrapped.
    """

    def __init__(self, obj, setup=None, cleanup=None, reset=None):
        """Create a MethodFixture.

        :param obj: The object to wrap. Exposed as fixture.obj
        :param setup: A method which takes no parameters. e.g.
            def setUp(self):
                self.value = 42
            If setup is not supplied, and the object has a setUp method, that
            method is used, otherwise nothing will happen during fixture.setUp.
        :param cleanup: Optional method to cleanup the object's state. If
            not supplied the method 'tearDown' is used if it exists.
        :param reset: Optional method to reset the wrapped object for use.
            If not supplied, then the method 'reset' is used if it exists,
            otherwise cleanUp and setUp are called as per Fixture.reset().
        """
        super(MethodFixture, self).__init__()
        self.obj = obj
        if setup is None:
            setup = getattr(obj, 'setUp', None)
            if setup is None:
                setup = lambda: None
        self._setup = setup
        if cleanup is None:
            cleanup = getattr(obj, 'tearDown', None)
            if cleanup is None:
                cleanup = lambda: None
        self._cleanup = cleanup
        if reset is None:
            reset = getattr(obj, 'reset', None)
        self._reset = reset

    def _setUp(self):
        self._setup()

    def cleanUp(self):
        super(MethodFixture, self).cleanUp()
        self._cleanup()

    def reset(self):
        if self._reset is None:
            super(MethodFixture, self).reset()
        else:
            self._reset()


class CompoundFixture(Fixture):
    """A fixture that combines many fixtures.

    :ivar fixtures: The list of fixtures that make up this one. (read only).
    """

    def __init__(self, fixtures):
        """Construct a fixture made of many fixtures.

        :param fixtures: An iterable of fixtures.
        """
        super(CompoundFixture, self).__init__()
        self.fixtures = list(fixtures)

    def _setUp(self):
        for fixture in self.fixtures:
            self.useFixture(fixture)
