'''
Classes and functions to define modes in scripts.
'''

__author__  = ['Miguel Ramos Pernas']
__email__   = ['miguel.ramos.pernas@cern.ch']


__all__ = ['extends', 'mode', 'Mode']


def extends( modes, kwargs=None, collision_policy=None ):
    '''
    Function to decorate a mode so it also expects the inputs of those
    specified in "modes".
    The argument "collision_policy" defines what to do in case two or
    more modes have the same arguments.
    It must be a function taking three arguments.
    The first one is the key, or name of the argument, the second is the
    current value of the argument, while the last one is that
    from the new mode being processed.
    The value of the argument is set to its output.
    By default, if two or more modes expect the same argument and the
    value is different for any of them, a :class:`RuntimeError`
    is raised.

    :param modes: modes to extend the decorated function with.
    :type modes: container(Mode)
    :param kwargs: extra keyword parameters to consider. These will be \
    extended to those taken from "modes".
    :type kwargs: dict
    :param collision_policy: functions defining the policy to use when two \
    or more modes expect the same arguments. It must be given as a \
    dictionary, where the key refers to the name of the argument and the \
    value is the function.
    :type collision_policy: dict
    :returns: result from calling :func:`mode` with keyword arguments.
    :rtype: function
    '''
    collision_policy = collision_policy or {}

    kwargs = kwargs or {}
    for m in modes:

        for k, v in m._kwargs.items():

            if k in kwargs:

                if k in collision_policy:
                    kwargs[k] = collision_policy[k](k, kwargs[k], v)
                elif kwargs[k] != v:
                    raise RuntimeError('Collision for key "{}", and no policy has been specified'.format(k))

            else:
                kwargs[k] = v

    return mode(**kwargs)


def mode( *args, **kwargs ):
    '''
    Decorator over a function to define a mode to run.
    Builds an instance of the class :class:`pyscripts.Mode`.

    :param kwargs: dictionary holding the different arguments that will \
    be passed to the decorated function.
    :type kwargs: dict
    :returns: proxy for the mode to run, or decorator to create a \
    :class:`Mode` instance from a function.
    :rtype: Mode or function
    '''
    err = ValueError('Function "mode" can only be called either taking a function or a set of keyword arguments')

    if len(args) == 1:

        if kwargs:
            raise err

        f = args[0]

        return Mode(f, kwargs)

    elif len(args) > 1:
        raise err
    else:
        def decorator( func ):
            return Mode(func, kwargs)

        return decorator


class Mode(object):

    def __init__( self, func, kwargs ):
        '''
        Represent a mode to be run on a script.
        To correctly decorate a function, use :func:`pyscripts.mode` instead.
        It holds the function and the information provided in "kwargs", which
        can be accessed either by index (using the method
        :method:`pyscripts.Mode.__getitem__`), or as an attribute:

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

        Both the name of the class and the docstring are changed to match that
        of the function.
        Note that the result of :python:`help(mode)` will still show the
        information about the :class:`pyscripts.Mode` class.
        These variables are stored so one can acccess the information of how
        to execute the function.

        :param func: function to call.
        :type func: function
        :param kwargs: dictionary holding the different arguments that will \
        be passed to the decorated function.
        :type kwargs: dict
        :returns: proxy of the mode to run.
        :rtype: Mode
        '''
        super(Mode, self).__init__()

        self._func   = func
        self._kwargs = kwargs

        # Store the name and change the docstring.
        self.__name__ = func.__name__
        self.__doc__  = func.__doc__

    def __call__( self, *args, **kwargs ):
        '''
        Call the function defining the global variables in the scope of the
        wrapped function.

        :returns: whatever the wrapped function returns.
        '''
        cm = set(self._kwargs.keys()).intersection(kwargs.keys())
        if cm:
            raise ValueError('Colliding keyword arguments: {}'.format(cm))

        kwargs.update(self._kwargs)

        return self._func(*args, **kwargs)

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
        return self._kwargs[arg]
