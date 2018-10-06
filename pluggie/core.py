import os
from types import Callable
from importlib import import_module
from inspect import signature, Parameter

from .excepions import *
import .validate


class Trigger:
    def __init__(self, generic_name, specific_name, pluggie):
        self._pluggie = pluggie
        self._generic_name = specific_name
        self._specific_name = generic_name
        self._callbacks = []
        self._description = ""
        self._f = None
        self._signature = None

    def __str__(self):
        return """Event `{}`
        Type: `{}`
        Target Signature: {}
        {}
        """.format(
            self.event_name, type(self), str(self._signature),
            self._description,
        )

    @property
    def event_name(self):
        return (
            "{}:{}".format(self._generic_name, self._specific_name)
            if self._specific_name else self._generic_name,
        )

    @property
    def func_name(self):
        if self._f is None:
            raise EventTriggerError("{} not properly setup", self.event_name)
        return self._f.__name__

    def setup(self, f):
        self._signature = signature(f)
        self._f = f
        if self._generic_name is None:
            self._generic_name = f.__name__
        self._pluggie.check_event_name_collision(self)
        return self.call

    def call(self, *args, **kwargs):
        raise NotImplementedException("{} doesn't implement `call`".format(
            type(self),
        ))

    def register(self, callback):
        self._callbacks.append(callback)

    def is_triggering(self, generic_name, specific_name=None):
        return (
            generic_name == self._generic_name
            and (
                specific_name is None
                or specific_name == self._specific_name
            )
        )


class PreProcessInputTrigger(Trigger):
    def __init__(self, generic_name, specific_name, pluggie):
        super(self, Trigger).__init__(generic_name, specific_name, pluggie)
        self._description = """
            All registered plugins to this event recieves the
            function arguments before the target function recieves
            them.

            The callback must implement the exact call interface of the target
            function and must return a two length tuple where the first item
            is the args list and the second the keyword args as a dict.

            Note that the args and keyword args don't have to be the same
            that the function recieved but needs to be a sufficent set to
            fulfill the signature of the target function.
        """

    def register(self, callback):
        validate.signature_args(self._signature, signature(callback))
        super(self, Trigger).register(callback)

    def call(self, *args, **kwargs):
        for callback in self._callbacks:
            args, kwargs = callback(*args, **kwargs)
            validate.args_against_signature(self._signature, *args, **kwargs)
        return self._f(*args, **kwargs)


class PostProcessResultTrigger(Trigger):
    def __init__(self, generic_name, specific_name, pluggie, validator=None):
        super(self, Trigger).__init__(generic_name, specific_name, pluggie)
        self._validator = validator
        self._description = """
            All registered plugins to this event recieves the
            function return values in sequence.

            The callback must implement implement the target function's
            return value signature as both its return value signature and
            the arguments signature.

            If a `validator` function is supplied at trigger setup, then
            it will be used to validate the return values.

            Else if no validator function and no type annotation is used,
            type consistency is verified.

            `validator`:

            A function that takes two arguments, initial return value and
            current return value and returns a boolean.

            Example validator of a function that returns a numpy array:

            ```
                import numpy as np
                def array_validator(
                    original: np.ndarray, current: np.ndarray,
                ) -> bool:
                    return (
                        original.shape == current.shape
                        original.dtype == current.dtype
                    )
            ```
        """

    def register(self, callback):
        sig = signature(callback)
        validate.return_types(self._signature, sig)
        validate.chainable(self._signature, sig)
        super(self, Trigger).register(callback)

    def call(self, *args, **kwargs):
        ret = self._f(*args, **kwargs)
        intermediate = ret
        for callback in self._callbacks:
            intermediate = callback(intermediate)
            if self._validator:
                if not self._validator(ret, intermediate):
                    raise SignatureError(
                        'Supplied validator rejected output of {} ({}) {} {}'
                        .format(
                            callback,
                            intermediate,
                            self.event_name,
                            self.func_name,
                        )
                    )
            else:
                validate.returned_objects(self._signature, ret, intermediate)
        return intermediate


class Pluggie:

    def __init__(self):
        self._event_triggers = []

    def check_event_name_collision(self, trigger):
        for t in self._event_triggers:
            if t is trigger:
                continue
            elif t.event_name == trigger.event_name:
                raise EventTriggerError(
                    "{} on {} duplicates event on {}".format(
                        t.event_name,
                        trigger.func_name,
                        t.func_name,
                ))

    def _add_event(self, TriggerClass, args):
        if len(args) == 1 and isinstance(args[0], Callable):
            trigger = TriggerClass(generic_name, specific_name, self)
            self._event_triggers.append(trigger)
            return trigger.setup(args[0])
        elif len(args) == 1:
            generic_name = args[0]
            specific_name = None
        elif len(args) == 2:
            generic_name, specific_name = args
        else:
            raise EventTriggerError("Can't setup {} using args {}".format(
                TriggerClass, args,
            ))
        trigger = TriggerClass(generic_name, specific_name, self)
        self._event_triggers.append(trigger)
        return trigger.setup

    def preprocess_event(self, *args):
        self._add_event(PreProcessInputTrigger, args)

    def load_plugin(self, name):
        path = os.path.join(
            os.environ.get('PLUGGIE_PLUGINS', 'plugins'),
            os.path.basename(name)
        )
        try:
            module = importlib.import_module(path)
        except ImportError:
            raise PluginLoadError('Could not locate plugin {}'.format(path))

        def gen():
            try:
                for event, callback in module.__PLUGGIE:
            except (AttributeError, IndexError, TypeError):
                raise PluginLoadError("")
            else:
                yield event, callback

        for event, callback in gen():
            self._register_plugin_callback(event, callback)

    def _register_plugin_callback(self, event_name, plugin_callback):
        name_tupe = event_name.split(':', 1)
        if len(name_tupe) == 2:
            generic_name, specific_name = name_tupe
        else:
            generic_name, = name_tupe
            specific_name = None

        for trigger in self._event_triggers:
            if trigger.is_triggering(generic_name, specific_name):
                trigger.register(plugin_callback)
