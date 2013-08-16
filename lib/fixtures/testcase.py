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
    'TestWithFixtures',
    ]

import unittest

from fixtures.fixture import gather_details


class TestWithFixtures(unittest.TestCase):
    """A TestCase with a helper function to use fixtures.
    
    Normally used as a mix-in class to add useFixture.

    Note that test classes such as testtools.TestCase which already have a
    ``useFixture`` method do not need this mixed in.
    """

    def useFixture(self, fixture):
        """Use fixture in a test case.

        The fixture will be setUp, and self.addCleanup(fixture.cleanUp) called.

        :param fixture: The fixture to use.
        :return: The fixture, after setting it up and scheduling a cleanup for
           it.
        """
        use_details = (
            gather_details is not None and
            getattr(self, "addDetail", None) is not None)
        try:
            fixture.setUp()
        except:
            if use_details:
                # Capture the details now, in case the fixture goes away.
                gather_details(fixture.getDetails(), self.getDetails())
            raise
        else:
            self.addCleanup(fixture.cleanUp)
            if use_details:
                # Capture the details from the fixture during test teardown;
                # this will evaluate the details before tearing down the
                # fixture.
                self.addCleanup(gather_details, fixture, self)
            return fixture
