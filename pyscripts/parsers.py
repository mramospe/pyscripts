'''
Define utils to parse arguments in the scripts.
'''

__author__  = ['Miguel Ramos Pernas']
__email__   = ['miguel.ramos.pernas@cern.ch']

# Python
import argparse
from collections import namedtuple

# Default name of the callable in the attributes of the Namespace
# obtained after processing the arguments.
CALLABLE_NAME = 'mode'


__all__ = ['CallArgsProxy', 'ModeArgumentParser', 'ModeParserProxy']


ModeParserProxy = namedtuple('ModeParserProxy', ['function', 'parser'])
ModeParserProxy.__new__.__doc__ = '''
Class representing an argument parser and a function associated to it.
'''

class CallArgsProxy(namedtuple('CallArgsProxy', ['function', 'args', 'unknown_args'])):

    def __call__( self ):
        '''
        Call the function with the arguments.
        '''
        return self.function(self.args)

    def __new__( cls, function, args, unknown_args = None ):
        '''
        Class representing an object storing a function and a set of parsed
        arguments.
        Only those in "args" will be passed to the function when called.

        :param function: function to execute.
        :type function: function
        :param args: arguments to call the function with.
        :type args: argparse.Namespace
        :param unknown_args: set of arguments which are unknown to the function.
        :type unknown_args: list
        '''
        return super(CallArgsProxy, cls).__new__(cls, function, args, unknown_args)


class ModeArgumentParser(argparse.ArgumentParser):

    def __init__( self, *args, **kwargs ):
        '''
        Define an argument parser that handles a script that is run with modes.
        It has some extra functionality that allows to automatically add modes
        from functions.
        The arguments are directly passed to the
        :class:`argparse.ArgumentParser` constructor.
        '''
        super(ModeArgumentParser, self).__init__(*args, **kwargs)

        self._callable_name = None
        self._modes         = {}

    def _mode_set_checker( method ):
        '''
        Checks whether the modes have been defined.

        :raises RuntimeError: If the modes have not been defined.
        '''
        def wrapper( self, *args, **kwargs ):
            '''
            Internal wrapper.
            '''
            if not self._modes:
                raise RuntimeError('Modes have not been defined yet')

            return method(self, *args, **kwargs)

        return wrapper

    @_mode_set_checker
    def _build_callable( self, args, unknown_args = None ):
        '''
        Build the callable object representing the function, known and unknown
        arguments.

        :param args: arguments to be used to build the class, containing the \
        function.
        :type args: argparse.Namespace
        :param unknown_args: list of unknown arguments.
        :type unknown_args: list or None
        :returns: proxy representing the function, known and unknown arguments.
        :rtype: CallArgsProxy
        '''
        dct = dict(vars(args))

        func = _transforming_namespace_to_dict(dct.pop(self._callable_name))
        args = argparse.Namespace(**dct)

        return CallArgsProxy(func, args, unknown_args)

    def define_modes( self, modes, callable_name = CALLABLE_NAME, defaults = None, apply_to_parsers = None ):
        '''
        Build subparsers in the given parser, from the given set of callables
        (modes) to run.
        The subparsers will have the name of the callables, and their description
        is taken directly from their docstrings.
        One can retrieve the single parser (per callable) as:

        >>> parser = pyscripts.ModeArgumentParser()
        >>> subparsers = parser.define_modes([func_1, func2])
        >>> parser_func_1 = subparsers.choices['func_1']
        >>> parser_func_2 = subparsers.choices['func_2']

        or via the :method:`pyscripts.ModeArgumentParser.mode` method:

        >>> parser_func_1 = parser.mode('func_1')
        >>> parser_func_2 = parser.mode('func_2')

        The callable is obtained after parsing the argument, and it is stored,
        by default, on the arguments namespace as "func".

        >>> parser = pyscripts.ModeArgumentParser()
        >>> parser.define_modes([func_1, func2])
        >>> args = parser.parse_args()

        then "args.function" will be the callable to call (func_1 or func_2, in
        this case).
        The stored function is not directly "func_1" or "func_2", but a simple
        wrapper around these functions which allows to give an instance of
        argparse.Namespace as the only argument.
        The wrapper will transform it into a dictionary, expanding its values
        and passing them to the desired functions.

        :param parser: parser where to add the subparsers.
        :type parser: ModeArgumentParser
        :param modes: collection of callables (modes) to add.
        :type modes: collection(callable)
        :param callable_name: name for the callable callable after parsing the \
        arguments.
        :type callable_name: str
        :param defaults: default arguments for the parsers. The name specified \
        in "callable_name" is reserved.
        :type defaults: dict or None
        :param apply_to_parsers: callable to call on each parser. It must take \
        a parser as the only argument.
        :type apply_to_parsers: callable or None
        :returns: collection of subparsers.
        :rtype: argparse._SubParsersAction
        '''
        subparsers = self.add_subparsers(title='Available modes', dest=CALLABLE_NAME)
        subparsers.required = True

        defaults = defaults if defaults is not None else {}

        self._callable_name = callable_name

        for m in modes:
            p = subparsers.add_parser(m.__name__, help=m.__doc__)

            defaults[callable_name] = m

            if apply_to_parsers is not None:
                apply_to_parsers(p)

            p.set_defaults(**defaults)

            self._modes[m.__name__] = ModeParserProxy(m, p)

        return subparsers

    @_mode_set_checker
    def mode( self, name ):
        '''
        Return the mode with name "name".

        :param name: name of the mode.
        :type name: str,
        :returns: proxy containing the function and parser of the mode with \
        the given name.
        :rtype: ModeParserProxy
        :raises RuntimeError: If the modes have not been defined yet.
        '''
        return self._modes[name]

    def parse_args_with_callable( self, *args, **kwargs ):
        '''
        Parse the arguments which are supposed to contain a callable
        member.
        This member should have been specified in
        :method:`pyscripts.ModeArgumentParser.define_modes`, using the
        "callable_name" argument.
        Forwards the inputs to :method:`argparse.ArgumentParser.parse_args`.

        :returns: proxy with the callable and the arguments.
        :rtype: CallArgsProxy
        :raises RuntimeError: If the modes have not been defined yet.
        '''
        args = self.parse_args(*args, **kwargs)

        return self._build_callable(args)

    def parse_known_args_with_callable( self, *args, **kwargs ):
        '''
        Parse the known arguments which are supposed to contain a callable
        member.
        This member should have been specified in
        :method:`pyscripts.ModeArgumentParser.define_modes`, using the
        "callable_name" argument.
        Forwards the inputs to :method:`argparse.ArgumentParser.parse_args`.

        :returns: proxy with the callable and the known and unknown arguments.
        :rtype: CallArgsProxy
        :raises RuntimeError: If the modes have not been defined yet.
        '''
        args, unknown = self.parse_known_args(*args, **kwargs)
        print(args, unknown)
        return self._build_callable(args, unknown)


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
