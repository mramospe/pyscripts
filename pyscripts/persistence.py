'''
Module to define classes and functions managing persistence of objects
in the scripts.
'''

__author__  = ['Miguel Ramos Pernas']
__email__   = ['miguel.ramos.pernas@cern.ch']

# Python
import functools
import os


__all__ = ['PersistenceDir', 'persisting_dir']


class PersistenceDir(object):

    def __init__( self, path ):
        '''
        Object to manage directories to store output files.
        At the time of construction, the input path is resolved, and
        directories are made following it.
        For each directory, a new :class:`pyscripts.PersistenceDir` object
        is created.

        :param path: root path for the class.
        :type path: str

        The usage is the following

        .. code-block: python

           >>> d = pyscripts.PersistenceDir('fdir')
           >>> sd = d['sdir']
           >>> d['sdir']
           PersistenceDir(path="fdir/sdir")
           >>> ssd = sd['ssdir/sssdir']
           >>> sd['ssdir']
           PersistenceDir(path="fdir/sdir/ssdir")
           >>> d['sdir/ssdir/sssdir']
           PersistenceDir(path="fdir/sdir/ssdir/sssdir")

        Absolute paths are not allowed.
        The directory tree must then start with a root, and the sub-directories
        must be under it.
        The name of the directories must be fully specified, i.e. paths like
        "../subdir/.." are not allowed.
        '''
        if not os.path.exists(path):
            os.makedirs(path)
        elif not os.path.isdir(path):
            raise RuntimeError(
                'Path "{}" exists and is not a directory'.format(path))

        self._path = path
        self._descendants = {}

    def __getitem__( self, path ):
        '''
        Given a path, create a :class:`pyscripts.PersistenceDir` if none of
        the objects are related to it.
        Otherwise, the already existing class is returned.

        :param path: path to the directory.
        :type str: str
        :returns: object of this class with the associated input path.
        :rtype: PersistenceDir
        '''
        if path.startswith('/') or './' in path:
            raise RuntimeError('Only relative paths are allowed in the form "subdir/subsubdir"')

        l = path.find('/')
        if l == -1:
            p = path
        else:
            p = path[:l]

        if p in self._descendants:
            # The base path already exists
            if l == -1:
                return self._descendants[p]
            else:
                return self._descendants[p][path[l + 1:]]

        # The path does not exist, we have to create it

        d = PersistenceDir(self.join(p))

        self._descendants[p] = d

        if l != -1:
            return d[path[l + 1:]]
        else:
            return d

    def __repr__( self ):
        '''
        Representation of this object.
        This is an alias to :meth:`pyscripts.PersistenceDir.__str__`.

        :returns: this object as a string.
        :rtype: str

        .. seealso:: :meth:`pyscripts.PersistenceDir.__str__`
        '''
        return self.__str__()

    def __str__( self ):
        '''
        Representation of this object as a string.
        The format is "<class name>(path="<path to the directory>")".

        :returns: this object as a string.
        :rtype: str
        '''
        return '{}(path="{}")'.format(self.__class__.__name__, self._path)

    def join( self, path ):
        '''
        Join the stored path with that given.

        :param path: input path.
        :type path: str
        :returns: joined path of that stored and that passed to the method.
        :rtype: str
        '''
        return os.path.join(self._path, path)

    def path( self ):
        '''
        Returns the path stored in the class.

        :returns: path stored in the class.
        :rtype: str
        '''
        return self._path


class persisting_dir(object):

    def __init__( self, arg, path = './', use_func_name = False ):
        '''
        Function to decorate a mode, so it will create a
        :class:`pyscripts.PersistenceDir` instance, and will be passed to the
        function using the keyword argument "arg".

        :param arg: name of the keyword argument to use.
        :type arg: str
        :param path: path where to do the persistence. By default use the \
        current directory.
        :type path: str
        :param use_func_name: if set to True, then the name of the function \
        will be added at the end of the given path.
        :type use_func_name: bool
        :returns: decorated function.
        :rtype: function
        :raises RuntimeError: if an attempt to override the keyword argument used \
        for the path is done.
        '''
        super(persisting_dir, self).__init__()

        self._arg  = arg
        self._path = path
        self._ufn  = use_func_name

    def __call__( self, mode ):
        '''
        Inner wrapper around the mode.
        '''
        if self._ufn:
            path = os.path.join(self._path, mode.__name__)
        else:
            path = self._path

        def __wrapper( *args, **kwargs ):
            '''
            Do the actual call to the function, using the given arguments.
            '''
            if self._arg in kwargs:
                raise RuntimeError('Defined keyword argument "{}" for path '\
                                   'persistence but is given as an input to '\
                                   'the function call')

            kwargs[self._arg] = PersistenceDir(path)

            return mode(*args, **kwargs)

        return __wrapper
