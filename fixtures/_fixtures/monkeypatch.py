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

import sys
import types

from fixtures import Fixture


def _coerce_values(obj, name, new_value, sentinel):
    """Handle value coercion for static and classmethods.

    setattr transforms a function into an instancemethod when set on a class.
    This checks if the attribute to be replaced is either and wraps new_value
    if necessary. This also checks getattr(obj, name) and wraps it if necessary
    since the staticmethod wrapper isn't preserved.
    """
    old_value = getattr(obj, name, sentinel)

    if sys.version_info[0] == 2:
        class_types = (type, types.ClassType)
    else:
        # All classes are <class 'type'> in Python 3
        class_types = type

    if not isinstance(obj, class_types):
        # Nothing special to do here
        return (new_value, old_value)

    # getattr() returns a function, this access pattern will return a
    # staticmethod/classmethod if the name method is defined that way
    old_attribute = obj.__dict__.get(name)
    if old_attribute is not None:
        old_value = old_attribute

    # If new_value is not callable it is potentially wrapped with staticmethod
    # or classmethod so grab the underlying function. If it has no underlying
    # callable thing the following coercion can be skipped, just return.
    if not callable(new_value):
        if hasattr(new_value, '__func__'):
            new_value = new_value.__func__
        else:
            return (new_value, old_value)

    if isinstance(old_value, staticmethod):
        new_value = staticmethod(new_value)
    if isinstance(old_value, classmethod):
        new_value = classmethod(new_value)
    if isinstance(old_value, types.FunctionType):
        captured_method = new_value
        def func_wrapper(*args, **kwargs):
            return captured_method(*args, **kwargs)
        new_value = func_wrapper

    return (new_value, old_value)


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
        new_value, old_value = _coerce_values(current, attribute,
                self.new_value, sentinel)
        if self.new_value is self.delete:
            if old_value is not sentinel:
                delattr(current, attribute)
        else:
            setattr(current, attribute, new_value)
        if old_value is sentinel:
            self.addCleanup(self._safe_delete, current, attribute)
        else:
            self.addCleanup(setattr, current, attribute, old_value)

    def _safe_delete(self, obj, attribute):
        """Delete obj.attribute handling the case where its missing."""
        sentinel = object()
        if getattr(obj, attribute, sentinel) is not sentinel:
            delattr(obj, attribute)
