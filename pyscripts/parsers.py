'''
Define utils to parse arguments in the scripts.
'''

__author__  = ['Miguel Ramos Pernas']
__email__   = ['miguel.ramos.pernas@cern.ch']

# Python
import argparse

# Default name of the callable in the attributes of the Namespace
# obtained after processing the arguments.
__callable_name__ = 'mode'


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
    func, nm = process_args(args, drop, call_name)

    return func(nm)


def define_modes( parser, modes, call_name = __callable_name__, defaults = None, apply_to_parsers = None ):
    '''
    Build subparsers in the given parser, from the given set of callables
    (modes) to run.
    The subparsers will have the name of the callables, and their description
    is taken directly from their docstrings.
    One can retrieve the single parser (per callable) as:

    >>> parser = argparse.ArgumentParser()
    >>> subparsers = define_modes(parser, [func_1, func2])
    >>> parser_func_1 = subparsers.choices['func_1']
    >>> parser_func_2 = subparsers.choices['func_2']

    By default, "func" will be the name associated to the callable execution,
    so after typing

    >>> parser = argparse.ArgumentParser()
    >>> define_modes(parser, [func_1, func2])
    >>> args = parser.parse_args()

    then "args.func" will be the callable to call (func_1 or func_2, in this
    case).
    The name of this attribute can be changed via "arg_mode".
    The stored function is not directly "func_1" or "func_2", but a simple
    wrapper around these functions which allows to give an instance of
    argparse.Namespace as the only argument.
    The wrapper will transform it into a dictionary, expanding its values and
    passing them to the desired functions.

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
    subparsers = parser.add_subparsers(title='Available modes', dest=__callable_name__)
    subparsers.required = True

    defaults = defaults if defaults is not None else {}

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
    A new argparse.Namespace instance is created and returned, together with
    the function to be called..

    :param args: arguments obtained from the parser.
    :type args: argparse.Namespace
    :param drop: values to drop.
    :type drop: list(str) or None
    :param call_name: name of the callable in the arguments.
    :type call_name: str
    :returns: function to execute and namespace holding the remaining values.
    :rtype: function, argparse.Namespace

    .. seealso:: :func:`call`
    '''
    dct = dict(vars(args))

    if drop is not None:
        for d in drop:
            dct.pop(d)

    func = _transforming_namespace_to_dict(dct.pop(call_name))

    nm = argparse.Namespace(**dct)

    return func, nm


def _transforming_namespace_to_dict( f ):
    '''
    Decorator which will return a function expecting an instance of the
    argparse.Namespace class.
    This instance will be parsed to extract its values to a dictionary,
    which is afterwards expanded and passed to the input function.

    :param f: function to decorate.
    :type f: function
    :returns: decorated function.
    :rtype: function
    '''
    def _wrapper( args ):
        '''
        Internal wrapper.
        '''
        return f(**vars(args))

    return _wrapper
