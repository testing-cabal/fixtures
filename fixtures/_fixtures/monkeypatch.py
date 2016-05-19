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

import functools
import sys
import types

from fixtures import Fixture


_class_types = (type, )
if getattr(types, 'ClassType', None):
    # Python 2 has multiple types of classes.
    _class_types = _class_types + (types.ClassType,)


def _coerce_values(obj, name, new_value, sentinel):
    """Return an adapted (new_value, old_value) for patching obj.name.
    
    setattr transforms a function into an instancemethod when set on a class.
    This checks if the attribute to be replaced is a callable descriptor -
    staticmethod, classmethod, or types.FunctionType - and wraps new_value if
    necessary.
    
    This also checks getattr(obj, name) and wraps it if necessary
    since the staticmethod wrapper isn't preserved.

    :param obj: The object with an attribute being patched.
    :param name: The name of the attribute being patched.
    :param new_value: The new value to be assigned.
    :param sentinel: If no old_value existed, the sentinel is returned to
        indicate that.
    """
    old_value = getattr(obj, name, sentinel)
    if not isinstance(obj, _class_types):
        # We may be dealing with an instance of a class. In that case the
        # attribute may be the result of a descriptor lookup (or a __getattr__
        # override etc). Its incomplete, but generally good enough to just
        # look and see if name is in the instance dict.
        try:
            obj.__dict__[name]
        except (AttributeError, KeyError):
            return (new_value, sentinel)
        else:
            return (new_value, old_value)

    # getattr() returns a function, this access pattern will return a
    # staticmethod/classmethod if the name method is defined that way
    old_attribute = obj.__dict__.get(name)
    if old_attribute is not None:
        old_value = old_attribute

    # If new_value is not callable, no special handling is needed.
    # (well, technically the same descriptor issue can happen with
    # user supplied descriptors, but that is arguably a feature - someone can
    # deliberately install a different descriptor.
    if not callable(new_value):
        return (new_value, old_value)

    if isinstance(old_value, staticmethod):
        new_value = staticmethod(new_value)
    elif isinstance(old_value, classmethod):
        new_value = classmethod(new_value)
    elif isinstance(old_value, types.FunctionType):
        if hasattr(new_value, '__get__'):
            # new_value is a descriptor, and that would result in it being
            # rebound if we assign it to a class - we want to preserve the
            # bound state rather than having it bound to the new object
            # it has been patched onto.
            captured_method = new_value
            @functools.wraps(old_value)
            def avoid_get(*args, **kwargs):
                return captured_method(*args, **kwargs)
            new_value = avoid_get

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

        When patching methods, the call signature of name should be a subset
        of the parameters which can be used to call new_value.

        For instance.

        >>> class T:
        ...     def method(self, arg1):
        ...         pass
        >>> class N:
        ...     @staticmethod
        ...     def newmethod(arg1):
        ...         pass

        Patching N.newmethod on top of T.method and then calling T().method(1)
        will not work because they do not have compatible call signatures -
        self will be passed to newmethod because the callable (N.newmethod)
        is placed onto T as a regular function. This allows capturing all the
        supplied parameters while still consulting local state in your
        new_value.
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
