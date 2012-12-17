#  fixtures: Fixtures with cleanups for testing and convenience.
#
# Copyright (c) 2012, Robert Collins <robertc@robertcollins.net>
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

from testtools import TestCase
from testtools.compat import (
    _b,
    _u,
    )
from testtools.matchers import Contains

from fixtures import (
    ByteStream,
    DetailStream,
    StringStream,
    )


class DetailStreamTest(TestCase):

    def test_doc_mentions_deprecated(self):
        self.assertThat(DetailStream.__doc__, Contains('Deprecated'))


class TestByteStreams(TestCase):

    def test_empty_detail_stream(self):
        detail_name = 'test'
        fixture = ByteStream(detail_name)
        with fixture:
            content = fixture.getDetails()[detail_name]
            self.assertEqual(_u(""), content.as_text())

    def test_stream_content_in_details(self):
        detail_name = 'test'
        fixture = ByteStream(detail_name)
        with fixture:
            stream = fixture.stream
            content = fixture.getDetails()[detail_name]
            # Output after getDetails is called is included.
            stream.write(_b("testing 1 2 3"))
            self.assertEqual("testing 1 2 3", content.as_text())

    def test_stream_content_reset(self):
        detail_name = 'test'
        fixture = ByteStream(detail_name)
        with fixture:
            stream = fixture.stream
            content = fixture.getDetails()[detail_name]
            stream.write(_b("testing 1 2 3"))
        with fixture:
            # The old content object returns the old usage
            self.assertEqual(_u("testing 1 2 3"), content.as_text())
            content = fixture.getDetails()[detail_name]
            # A new fixture returns the new output:
            stream = fixture.stream
            stream.write(_b("1 2 3 testing"))
            self.assertEqual(_u("1 2 3 testing"), content.as_text())


class TestStringStreams(TestCase):

    def test_empty_detail_stream(self):
        detail_name = 'test'
        fixture = StringStream(detail_name)
        with fixture:
            content = fixture.getDetails()[detail_name]
            self.assertEqual(_u(""), content.as_text())

    def test_stream_content_in_details(self):
        detail_name = 'test'
        fixture = StringStream(detail_name)
        with fixture:
            stream = fixture.stream
            content = fixture.getDetails()[detail_name]
            # Output after getDetails is called is included.
            stream.write(_u("testing 1 2 3"))
            self.assertEqual("testing 1 2 3", content.as_text())

    def test_stream_content_reset(self):
        detail_name = 'test'
        fixture = StringStream(detail_name)
        with fixture:
            stream = fixture.stream
            content = fixture.getDetails()[detail_name]
            stream.write(_u("testing 1 2 3"))
        with fixture:
            # The old content object returns the old usage
            self.assertEqual(_u("testing 1 2 3"), content.as_text())
            content = fixture.getDetails()[detail_name]
            # A new fixture returns the new output:
            stream = fixture.stream
            stream.write(_u("1 2 3 testing"))
            self.assertEqual(_u("1 2 3 testing"), content.as_text())
