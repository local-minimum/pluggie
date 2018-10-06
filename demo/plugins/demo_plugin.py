def preprocessor(a, b=5):
    return (2*a,), {'b': b - 2}
    

__PLUGGIE = [
    ('my_function', preprocessor)
]
