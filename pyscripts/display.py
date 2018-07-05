'''
Functions to manage the display or redirection of the streams to files,
stdout, stderr, etc.
'''

__author__  = ['Miguel Ramos Pernas']
__email__   = ['miguel.ramos.pernas@cern.ch']


# Python
import io
from contextlib import contextmanager

__all__ = ['stdout_redirector']


@contextmanager
def stdout_redirector( stream = None ):
    '''
    Redirect stdout to the given stream.
    The call to this function opens a new context, so you can write:

    >>> with stdout_redirector() as out:
    >>>     # whatever is printed here will go to "out"
    >>>     print('Hello')
    >>>     out.seek(0)
    >>>     captured = out.read()
    >>> print(captured)
    Hello

    :param stream: object to collect the output stream.
    :type stream: file
    :returns: output stream (io.BytesIO by default).
    :rtype: file
    '''
    stream = stream if stream is not None else io.BytesIO()

    # The original fd stdout points to
    original_stdout_fd = sys.stdout.fileno()

    def _redirect_stdout( to_fd ):
        '''
        Redirect stdout to the given file descriptor.
        '''
        # Flush the C-level buffer stdout
        libc = ctypes.CDLL(None)
        c_stdout = ctypes.c_void_p.in_dll(libc, 'stdout')
        libc.fflush(c_stdout)

        # Flush and close sys.stdout - also closes the file descriptor (fd)
        sys.stdout.close()

        # Make original_stdout_fd point to the same file as to_fd
        os.dup2(to_fd, original_stdout_fd)

        # Create a new sys.stdout that points to the redirected fd
        c = io.FileIO(original_stdout_fd, 'wb')
        sys.stdout = io.TextIOWrapper(c)

    # Save a copy of the original stdout fd in saved_stdout_fd
    saved_stdout_fd = os.dup(original_stdout_fd)

    try:

        # Create a temporary file and redirect stdout to it
        tfile = tempfile.TemporaryFile(mode='w+b')
        _redirect_stdout(tfile.fileno())

        # Yield to caller, then redirect stdout back to the saved fd
        yield stream
        _redirect_stdout(saved_stdout_fd)

        # Copy contents of temporary file to the given stream
        tfile.flush()
        tfile.seek(0, io.SEEK_SET)
        stream.write(tfile.read())

    finally:
        tfile.close()
        os.close(saved_stdout_fd)
