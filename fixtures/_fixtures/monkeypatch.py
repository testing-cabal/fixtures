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
    'MonkeyPatch'
    ]

import inspect
import sys
import types

from fixtures import Fixture


def _setattr(obj, name, value, check_value=False):
    """Handle some corner cases when calling setattr.

    setattr transforms a function into instancemethod when set on a class, so
    where appropriate value needs to be wrapped with staticmethod().
    """
    if sys.version_info[0] == 2:
        class_types = (type, types.ClassType)
        py2 = True
    else:
        # All classes are <class 'type'> in Python 3
        class_types = type
        py2 = False

    if not isinstance(obj, class_types):
        # Nothing special to do here
        setattr(obj, name, value)
        return

    # Check if 'name' is an instancemethod and if so convert 'value' to match.
    # if check_value == True we check 'value' instead.
    if not check_value:
        attr_to_check = getattr(obj, name, None)
    else:
        attr_to_check = value
    if py2:
        # Python2 distinguishes between instance and staticmethods on a class
        # definition
        if isinstance(attr_to_check, types.FunctionType):
            value = staticmethod(value)
    else:
        # Python3 only distinguishes between instance and staticmethods on a
        # constructed class. Assume standard naming conventions and check for
        # 'self' as the first parameter.
        args = inspect.getfullargspec(attr_to_check).args
        if len(args) == 0 or 'self' not in args[0]:
            value = staticmethod(value)
    setattr(obj, name, value)


class MonkeyPatch(Fixture):
    """Replace or delete an attribute."""

    delete = object()

    def __init__(self, name, new_value=None):
        """Create a MonkeyPatch.

        :param name: The fully qualified object name to override.
        :param new_value: A value to set the name to. If set to
            MonkeyPatch.delete the attribute will be deleted.

        During setup the name will be deleted or assigned the requested value,
        and this will be restored in cleanUp.
        """
        Fixture.__init__(self)
        self.name = name
        self.new_value = new_value
    
    def _setUp(self):
        location, attribute = self.name.rsplit('.', 1)
        # Import, swallowing all errors as any element of location may be
        # a class or some such thing.
        try:
            __import__(location, {}, {})
        except ImportError:
            pass
        components = location.split('.')
        current = __import__(components[0], {}, {})
        for component in components[1:]:
            current = getattr(current, component)
        sentinel = object()
        old_value = getattr(current, attribute, sentinel)
        if self.new_value is self.delete:
            if old_value is not sentinel:
                delattr(current, attribute)
        else:
            _setattr(current, attribute, self.new_value)
        if old_value is sentinel:
            self.addCleanup(self._safe_delete, current, attribute)
        else:
            self.addCleanup(_setattr, current, attribute, old_value,
                    check_value=True)

    def _safe_delete(self, obj, attribute):
        """Delete obj.attribute handling the case where its missing."""
        sentinel = object()
        if getattr(obj, attribute, sentinel) is not sentinel:
            delattr(obj, attribute)
