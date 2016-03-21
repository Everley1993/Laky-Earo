#!/usr/bin/python
# -*- coding:utf-8 -*-

import inspect
import traceback
from datetime import datetime


class NoEmittion(object):

    def __init__(self, event_cls, msg):
        self.event_cls = event_cls
        self.msg = msg


class Emittion(object):

    def __init__(self, event):
        self.event = event


class HandlerRuntime(object):

    def __init__(self, handler, event):
        self.handler = handler
        self.event = event
        self.begin_time = None
        self.end_time = None
        self.exception = None
        self.no_emittion = {}
        self.emittion = []

    @property
    def succeeded(self):
        return self.begin_time is not None and self.end_time is not None and self.exception is None

    def record_begin_time(self):
        self.begin_time = datetime.now()

    def record_end_time(self):
        self.end_time = datetime.now()

    def record_exception(self, exception):
        self.exception = exception

    def record_emittion(self, emittion):
        self.emittion.append(emittion.event)

    def record_no_emittion(self, no_emittion):
        self.no_emittion[no_emittion.event_cls] = no_emittion.msg

    def why_no_emittion(self, event_cls):
        return self.no_emittion[event_cls] \
            if event_cls in self.no_emittion else None

    @property
    def time_cost(self):
        if self.begin_time is not None and self.end_time is not None:
            return (self.end_time - self.begin_time).microseconds
        else:
            return -1


class Handler(object):

    def __init__(self, event_cls, func, emit_events=list()):

        self.event_cls = event_cls
        self._validate_func(func)
        self.func = func
        self.emit_events = emit_events

    def _validate_func(self, handle_func):

        argspec = inspect.getargspec(handle_func)
        if argspec.args != ['context', 'event']:
            raise TypeError(
                'Handler\'s function must be function_name(context, event)')

    def handle(self, context, event):

        if not isinstance(event, self.event_cls):
            raise TypeError(
                'Handle unexcepted event %s. Except %s.' %
                (type(event), self.event_cls))

        handler_runtime = HandlerRuntime(self, event)
        try:
            handler_runtime.record_begin_time()
            results = self.func(context, event)
            if not hasattr(results, '__iter__'):
                results = (results, )
            for result in results:
                if isinstance(result, NoEmittion):
                    handler_runtime.record_no_emittion(result)
                elif isinstance(result, Emittion):
                    handler_runtime.record_emittion(result)
        except Exception as e:
            e.traceback = traceback.format_exc()
            handler_runtime.record_exception(e)
        finally:
            handler_runtime.record_end_time()
            return handler_runtime

    def __eq__(self, obj):
        return isinstance(obj, Handler) \
            and self.event_cls == obj.event_cls \
            and self.func == obj.func \
            and self.emit_events == obj.emit_events

    def __str__(self):
        return '%s.%s:%s.%s' % (self.event_cls.__module__,
                                self.event_cls.__name__,
                                self.func.__module__,
                                self.func.__name__)

    def __repr__(self):
        return self.__str__()