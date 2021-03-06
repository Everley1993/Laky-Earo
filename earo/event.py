#!/usr/bin/python
# -*- coding:utf-8 -*-

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#   Copyright 2016 Everley                                                    #
#                                                                             #
#   Licensed under the Apache License, Version 2.0 (the "License");           #
#   you may not use this file except in compliance with the License.          #
#   You may obtain a copy of the License at                                   #
#                                                                             #
#       http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                             #
#   Unless required by applicable law or agreed to in writing, software       #
#   distributed under the License is distributed on an "AS IS" BASIS,         #
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#   See the License for the specific language governing permissions and       #
#   limitations under the License.                                            #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

import copy


class Field(object):
    """
    The field object of :class:`Event`.
    """

    field_type = None
    """
    The class of the field.
    """

    default = None
    """
    The default value of the filed.
    """

    def __init__(self, field_type, default=None):

        self.field_type = field_type
        self.default = default
        self.match(default)

    def match(self, value):
        """
        Raise an :class:`TypeError` is `value` is not an instance of `self.field_type`.

        :param value: The value to match.
        """
        if value is not None and not isinstance(value, self.field_type):
            raise TypeError('expect %s, not %s' %
                            (self.field_type, type(value)))


class EventMetaClass(type):
    """
    The metaclass to help new :class:`Event`.
    """

    def __new__(cls, name, bases, attrs):

        fields = []
        mappings = {}
        params = {}
        new_attrs = {}
        for k, v in attrs.items():
            if isinstance(v, Field):
                fields.append(v)
                mappings[k] = v
                params[k] = v.default
            else:
                new_attrs[k] = v
        new_attrs['__fields__'] = fields
        new_attrs['__mappings__'] = mappings
        new_attrs['__params__'] = params
        new_attrs['__actual_params__'] = None
        new_attrs['__tag__'] = attrs['__tag__'] \
            if '__tag__' in attrs else ''
        new_attrs['__description__'] = attrs['__description__'] \
            if '__description__' in attrs else ''
        return super(EventMetaClass, cls).__new__(cls, name, bases, new_attrs)


class Event(object):
    """
    The base class of specific event.
    """

    __metaclass__ = EventMetaClass

    def __init__(self, **kwargs):
        self.__actual_params__ = copy.deepcopy(self.__params__)
        for k, v in kwargs.iteritems():
            self.__setattr__(k, v)

    def __getattr__(self, key):
        if key in self.__actual_params__:
            return self.__actual_params__[key]
        else:
            raise AttributeError(
                "%s has no param `%s`" %
                (type(self), key))

    def __setattr__(self, key, value):
        if key in ['__actual_params__']:
            return super(Event, self).__setattr__(key, value)
        if key in self.__actual_params__:
            self.__mappings__[key].match(value)
            self.__actual_params__[key] = value
        else:
            raise AttributeError(
                "%s has no param `%s`" %
                (type(self), key))

    @property
    def params(self):
        """
        A `dict` which is a deep copy of the event's params.
        """
        return copy.deepcopy(self.__actual_params__)

    @classmethod
    def tag(cls):
        """
        The tag of the event.
        """
        return cls.__tag__

    @classmethod
    def description(cls):
        """
        The description of the event.
        """
        return cls.__description__

    @classmethod
    def key(cls):
        """
        A unique string for the event.
        """
        return '%s.%s' % (cls.__module__, cls.__name__)

    @property
    def no_field(self):
        """
        return True if the event doesn't have any field.
        """
        return len(self.__params__) == 0
