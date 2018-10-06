from pluggie import Pluggie

plug = Pluggie()


@plug.preprocess_event
def my_function(a, b=1):
    print("a={}, b={}".format(a, b))
    return a * b

assert my_function(2) == 2
plug.load_plugin('demo_plugin.py')
assert my_function(2) == 12
assert my_function(2, b=1) == -4
