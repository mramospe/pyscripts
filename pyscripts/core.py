'''
Helper functions and decorators.
'''

__author__ = 'Miguel Ramos Pernas'
__email__  = 'miguel.ramos.pernas@cern.ch'

# Python
import functools


__all__ = ['run_once']


def decorate( deco ):
    '''
    Decorate using the given function, preserving the docstring.

    :param deco: decorator.
    :type deco: function
    :returns: function used to decorate.
    :rtype: function
    '''
    def _wrapper( f ):
        '''
        Wrap the decorator.
        '''
        @functools.wraps(f)
        def __wrapper( *args, **kwargs ):
            '''
            Inner wrapper which actually calls the function.
            '''
            return deco(f)(*args, **kwargs)

        return __wrapper

    return _wrapper


def run_once( func ):
    '''
    Decorator to make a function run only once.
    This is achieved by creating a new attribute "has_run", in the function
    wrapper.

    :param func: function to decorate.
    :type func: function
    :returns: decorated function.
    :rtype: function
    '''
    @functools.wraps(func)
    def wrapper( *args, **kwargs ):
        '''
        Wrapper around "func".
        '''
        if wrapper.has_run == False:
            wrapper.has_run = True
            return func(*args, **kwargs)

    wrapper.has_run = False

    return wrapper
