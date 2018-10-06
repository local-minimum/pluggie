from .exceptions import SignatureError


def signature_args(refsig, sig):
    if list(refsig.parameters.keys()) != list(sig.parameters.keys()):
        raise SignatureError('Missmatch in parameters {} expected {}'.format(
            refsig.parameters.keys(), sig.parameters.keys(),
        ))
    for param1, param2 in zip(
        refsig.parameters.values(), sig.parameters.values(),
    ):
        if (param1.kind != param2.kind):
            raise SignatureError(
                '{} was expected to be of kind {} not {}'.format(
                    param2.name, param1.kind, param2.kind,
                )
            )
        if (
            param1.annotation != param1.empty
            and param1.annotation != param2.annotation
        ):
            raise SignatureError('{} must have annotation {}, not {}'.format(
                param2.name,
                param1.annotation,
                param2.annotation,
            ))


def return_types(refsig, sig):
    pass


def _deeptype(obj):
    pass


def returned_objects(refsig, original, intermediate):
    if refsig.return_annotation != refsig.empty:
        # check intermediate is valid for refsig.return_annotation
        pass
    elif (_deeptype(original) != _deeptype(intermediate)):
        raise SignatureError()


def chainable(refsig, sig):
    pass


def args_against_signature(sig, *args, **kwargs):
    # TODO: Read up on new signatures
    # Test minimum args requirement
    position_only = [
        p for p in sig.parameters.values()
        if p.kind == p.POSITIONAL_ONLY
    ]
    if len(args) < len(position_only):
        raise SignatureError('Returned arguments not sufficient for function')

    # Test
    pass
