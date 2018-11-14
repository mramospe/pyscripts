'''
Classes and functions to define modes in scripts.
'''

__author__  = ['Miguel Ramos Pernas']
__email__   = ['miguel.ramos.pernas@cern.ch']

# Python
from functools import wraps


__all__ = ['mode', 'Mode']


def mode( *args, **kwargs ):
    '''
    Decorator over a function to define a mode to run.
    Builds an instance of the class :class:`pyscripts.Mode`.

    :param kwargs: dictionary holding the different arguments that will \
    be passed to the decorated function.
    :type kwargs: dict
    :returns: proxy of the mode to run.
    :rtype: Mode
    '''
    err = ValueError('Function "mode" can only be called either taking a function or a set of keyword arguments')

    if len(args) == 1 is not None:

        if kwargs:
            raise err

        f = args[0]

        return wraps(f)(Mode(f, kwargs))

    elif len(args) > 1:
        raise err
    else:
        def decorator( func ):
            return wraps(func)(Mode(func, kwargs))

        return decorator


class Mode(object):

    def __init__( self, func, kwargs ):
        '''
        Represent a mode to be run on a script.
        To correctly decorate a function, use :func:`pyscripts.mode` instead.
        It holds a name, which by default is set to that of the function,
        and the information provided in "kwargs", which can be accessed
        either by index (using the method :method:`pyscripts.Mode.__getitem__`),
        or as an attribute:

        .. code-block:: python

           >>> @mode(inputs={'input_file': 'file.txt'})
           ... def foo( inputs ):
           ...     print(inputs)
           ...
           >>> foo()
           {'input_file': 'file.txt'}
           >>> foo['inputs']
           {'input_file': 'file.txt'}
           >>> foo.inputs
           {'input_file': 'file.txt'}

        :param func: function to call.
        :type func: function
        :param kwargs: dictionary holding the different arguments that will \
        be passed to the decorated function.
        :type kwargs: dict
        :returns: proxy of the mode to run.
        :rtype: Mode
        '''
        super(Mode, self).__init__()

        self.__func   = func
        self.__kwargs = kwargs

    def __call__( self, *args, **kwargs ):
        '''
        Call the function defining the global variables in the scope of the
        wrapped function.

        :returns: whatever the wrapped function returns.
        '''
        cm = set(self.__kwargs.keys()).intersection(kwargs.keys())
        if cm:
            raise ValueError('Colliding keyword arguments: {}'.format(cm))

        kwargs.update(self.__kwargs)

        return self.__func(*args, **kwargs)

    def __getattr__( self, arg ):
        '''
        Get the value of the argument to be passed to the function with name
        "arg".

        :param arg: name of the argument.
        :type arg: str
        :returns: value of the argument passed to the function.
        '''
        return self.__getitem__(arg)

    def __getitem__( self, arg ):
        '''
        Get the value of the argument to be passed to the function with name
        "arg".

        :param arg: name of the argument.
        :type arg: str
        :returns: value of the argument passed to the function.
        '''
        return self.__kwargs[arg]
