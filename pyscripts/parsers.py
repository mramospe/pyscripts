'''
Define utils to parse arguments in the scripts.
'''

__author__  = ['Miguel Ramos Pernas']
__email__   = ['miguel.ramos.pernas@cern.ch']


# Default name of the callable in the attributes of the Namespace
# obtained after processing the arguments.
__callable_name__ = 'func'


__all__ = ['call', 'define_modes', 'process_args']


def call( args, drop = None, call_name = __callable_name__ ):
    '''
    Process the callable after dropping some values in the arguments.
    The callable is expected to take the remaining values.

    :param args: arguments obtained from the parser.
    :type args: argparse.Namespace
    :param drop: values to drop.
    :type drop: list(str) or None
    :param call_name: name of the callable in the arguments.
    :type call_name: str
    :returns: whatever is returned in the callable call.

    .. seealso:: :func:`process_args`
    '''
    dct = process_args(args, drop, call_name)

    return getattr(args, call_name)(**dct)


def define_modes( parser, modes, call_name = __callable_name__, defaults = None, apply_to_parsers = None ):
    '''
    Build subparsers in the given parser, from the given set of callables
    (modes) to run.
    The subparsers will have the name of the callables, and their description
    is taken directly from their docstrings.
    One can retrieve the single parser (per callable) as:

    >>> parser = argparser.ArgumentParser()
    >>> subparsers = make_subparsers(parser, [func_1, func2])
    >>> parser_func_1 = subparsers.choices['func_1']
    >>> parser_func_2 = subparsers.choices['func_2']

    By default, "func" will be the name associated to the callable execution,
    so after typing

    >>> parser = argparser.ArgumentParser()
    >>> make_subparsers(parser, [func_1, func2])
    >>> args = parser.parse_args()

    then "args.func" will be the callable to call (func_1 or func_2, in this
    case). The name of this attribute can be changed via the "arg_mode".

    :param parser: parser where to add the subparsers.
    :type parser: argparse.ArgumentParser
    :param modes: collection of callables (modes) to add.
    :type modes: collection(callable)
    :param call_name: name for the callable callable after parsing the \
    arguments.
    :type call_name: str
    :param defaults: default arguments for the parsers. The name specified in \
    "call_name" is reserved.
    :type defaults: dict or None
    :param apply_to_parsers: callable to call on each parser. It must take a \
    parser as the only argument.
    :type apply_to_parsers: callable or None
    :returns: collection of subparsers.
    :rtype: argparse._SubParsersAction
    '''
    subparsers = parser.add_subparsers()

    for m in modes:
        p = subparsers.add_parser(m.__name__, help=m.__doc__)

        defaults[call_name] = m

        if apply_to_parsers is not None:
            apply_to_parsers(p)

        p.set_defaults(**defaults)

    return subparsers


def process_args( args, drop = None, call_name = __callable_name__ ):
    '''
    Process the arguments obtained by
    :meth:`argparse.ArgumentParser.parse_args`, dropping from its values
    everything specified in "drop" and "call_name".
    A dictionary is returned instead.

    :param args: arguments obtained from the parser.
    :type args: argparse.Namespace
    :param drop: values to drop.
    :type drop: list(str) or None
    :param call_name: name of the callable in the arguments.
    :type call_name: str
    :returns: dictionary with the remaining values.
    :rtype: dict

    .. seealso:: :func:`call`
    '''
    dct = dict(vars(args))

    if drop is not None:
        for d in drop:
            dct.pop(d)

    dct.pop(call_name)

    return dct
