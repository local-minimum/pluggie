_At this moment, this is just an experiment and something to do on the commute
train... it might prove useful in the future, but not yet_

# The idea
* Adding plugin support to an app should be as easy as decorating a function.
* Getting basic documentation of what events the plugins could hook into should
be automatic.
* Writing a plugin should require very little understanding of the plugin system.
* There should be some moderate level of security and validation of what
the plugins can do.

# How it would look setting up for plugins

```python
from pluggie import Pluggie

plug = Pluggie()


@plug.preprocess_event
def my_function(a, b=1):
    return a * b
```

or if you rather specify the name of the event instead of using the function
name...

```python
@plug.preprocess_event('test', 'before')
def my_function2(a, b=1):
    return a * b
```

Would generate an event trigger 'test:before'.

# How you would write a plugin

```python
def preprocessor(a, b=5):
    return (2*a,), {'b': b - 2}


__PLUGGIE = [
    ('my_function', preprocessor),
    ('test:before', preprocessor),
]
```
