'''
Functions to manage the display or redirection of the streams to files,
stdout, stderr, etc.
'''

__author__  = ['Miguel Ramos Pernas']
__email__   = ['miguel.ramos.pernas@cern.ch']


# Python
import ctypes
import functools
import io
import os
import sys
import tempfile
from contextlib import contextmanager


__all__ = ['redirect_stdstream']


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


@decorate(contextmanager)
def redirect_stdstream( istream = 'stdout', ostream = None, stream_type = 't' ):
    '''
    Redirect the information going to "istream" to the given stream.

    :param istream: where to redirect the output from. It can be any of \
    "stdout" or "stderr".
    :type istream: str
    :param ostream: object to collect the output stream.
    :type ostream: file
    :param stream_type: type of stream. 'b' if it works with byte objects or \
    't' if it does it with strings.
    :type stream_type: str
    :returns: output stream (:class:`io.StringIO` by default).
    :rtype: io.StringIO or file
    :raises ValueError: if an incorrect input stream name or type is provided.

    The call to this function opens a new context, so you can write:

    >>> with redirect_stdstream() as out:
    ...     # Whatever is printed here will go to "out"
    ...     print('Hello')
    ...
    >>> out.seek(0)
    >>> captured = out.read()
    >>> print(captured)
    'Hello'

    By default, it returns an :class:`io.StringIO` object.
    If you are working with the :mod:`logging` package, beware that you might
    have to define a special :class:`logging.Logger` instance for the messages
    sent within the duration of the context.
    For example, take a look at the following code:

    >>> with pyscripts.redirect_stdstream('stdout') as stdout, pyscripts.redirect_stdstream('stderr') as stderr:
    ...     #
    ...     # Define the logger
    ...     #
    ...     logger = logging.getLogger('test')
    ...     logger.setLevel(logging.INFO)
    ...     #
    ...     # Define the handler for "stdout"
    ...     #
    ...     hi = logging.StreamHandler(stdout)
    ...     hi.setLevel(logging.INFO)
    ...     #
    ...     # Define the handler for "stderr"
    ...     #
    ...     he = logging.StreamHandler(stderr)
    ...     he.setLevel(logging.WARNING)
    ...     #
    ...     # Define the formatter
    ...     #
    ...     f = logging.Formatter('%(levelname)s: %(message)s')
    ...     hi.setFormatter(f)
    ...     he.setFormatter(f)
    ...     #
    ...     # Add handlers
    ...     #
    ...     logger.addHandler(hi)
    ...     logger.addHandler(he)
    ...     #
    ...     # Display some messages
    ...     #
    ...     logger.info('information')
    ...     logger.error('error')
    ...
    >>> stdout.seek(0)
    >>> stdout.readlines()
    ['INFO: information\\n', 'ERROR: error\\n']
    >>> stderr.seek(0)
    >>> stderr.readlines()
    ['ERROR: error\\n']

    Beware that the :mod:`logging` package uses strings.
    If a byte-like working object is passed to :func:`redirect_stdstream`, the
    execution will probably crash.

    .. warning::
       The call to this function will temporary close "sys.stdout" or
       "sys.stderr", and will assign a new stream to them. Any object doing
       operations on the old streams will most likely cause an error.
    '''
    choices = ('stdout', 'stderr')
    if istream not in choices:
        raise ValueError('Unknown stream "{}"; please select any of '\
                         'the following: {}'.format(istream, choices))

    choices = ('t', 'b')
    if stream_type not in choices:
        raise ValueError('Unknown stream type "{}"; please select any of '\
                         'the following: {}'.format(stream_type, choices))

    ostream = ostream if ostream is not None else io.StringIO()

    # The original fd stream points to
    original_stream_fd = getattr(sys, istream).fileno()

    def _redirect( to_fd, istream ):
        '''
        Redirect "istream" to the given file descriptor.
        '''
        # Flush the C-level buffer stream
        libc = ctypes.CDLL(None)
        c_stream = ctypes.c_void_p.in_dll(libc, istream)
        libc.fflush(c_stream)

        # Flush and close sys.<stream> - also closes the file descriptor (fd)
        getattr(sys, istream).close()

        # Make original_stream_fd point to the same file as to_fd
        os.dup2(to_fd, original_stream_fd)

        # Create a new sys.<stream> that points to the redirected fd
        c = io.FileIO(original_stream_fd, 'wb')
        setattr(sys, istream, io.TextIOWrapper(c))

    # Save a copy of the original stream fd in saved_stream_fd
    saved_stream_fd = os.dup(original_stream_fd)

    try:

        # Create a temporary file and redirect stream to it
        tfile = tempfile.TemporaryFile(mode='w+{}'.format(stream_type))

        _redirect(tfile.fileno(), istream)

        # Yield to caller
        yield ostream

        # Redirect stream back to the saved fd
        _redirect(saved_stream_fd, istream)

        # Copy contents of temporary file to the given stream
        tfile.flush()
        tfile.seek(0, io.SEEK_SET)
        ostream.write(tfile.read())

    finally:
        tfile.close()
        os.close(saved_stream_fd)
