# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# Copyright 2013 Hewlett-Packard Development Company, L.P.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import extras

import fixtures

mock = extras.try_imports(['mock', 'unittest.mock'], None)
mock_default = extras.try_imports(
    ['mock.DEFAULT', 'unittest.mock.DEFAULT'], None)


class _Base(fixtures.Fixture):
    def _setUp(self):
        _p = self._get_p()
        self.addCleanup(_p.stop)
        self.mock = _p.start()


class MockPatchObject(_Base):
    """Deal with code around mock."""

    def __init__(self, obj, attr, new=mock_default, **kwargs):
        super(MockPatchObject, self).__init__()
        self._get_p = lambda: mock.patch.object(obj, attr, new, **kwargs)


class MockPatch(_Base):
    """Deal with code around mock.patch."""

    def __init__(self, obj, new=mock_default, **kwargs):
        super(MockPatch, self).__init__()
        self._get_p = lambda: mock.patch(obj, new, **kwargs)


class MockPatchMultiple(_Base):
    """Deal with code around mock.patch.multiple."""

    # Default value to trigger a MagicMock to be created for a named
    # attribute.
    DEFAULT = mock_default

    def __init__(self, obj, **kwargs):
        """Initialize the mocks

        Pass name=value to replace obj.name with value.

        Pass name=Multiple.DEFAULT to replace obj.name with a
        MagicMock instance.

        :param obj: Object or name containing values being mocked.
        :type obj: str or object
        :param kwargs: names and values of attributes of obj to be mocked.

        """
        super(MockPatchMultiple, self).__init__()
        self._get_p = lambda: mock.patch.multiple(obj, **kwargs)
