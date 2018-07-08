'''
Script to test the behaviour of the "redirect_stdstream" function.
'''

# Python
import argparse
import ctypes
import logging
import pytest
import tempfile

# Local
import pyscripts


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('library', type=str,
                        help='Path to the library')

    args = parser.parse_args()

    lib = ctypes.CDLL(args.library)

    # Default redirector
    with pyscripts.redirect_stdstream() as f:

        print('hello')
        lib.display(b'hello\n')

    f.seek(0)
    a = f.readlines()

    assert a == ['hello\n', 'hello\n']

    # Redirect to stderr with a logger (need to use strings)
    with pyscripts.redirect_stdstream('stdout') as stdout, pyscripts.redirect_stdstream('stderr') as stderr:

        logger = logging.getLogger('test')
        logger.setLevel(logging.INFO)

        hi = logging.StreamHandler(stdout)
        hi.setLevel(logging.INFO)

        he = logging.StreamHandler(stderr)
        he.setLevel(logging.WARNING)

        f = logging.Formatter('%(levelname)s: %(message)s')
        hi.setFormatter(f)
        he.setFormatter(f)

        logger.addHandler(hi)
        logger.addHandler(he)

        logger.info('information')
        logger.error('error')

    stdout.seek(0)
    a = stdout.readlines()
    assert a == ['INFO: information\n', 'ERROR: error\n']

    stderr.seek(0)
    a = stderr.readlines()
    assert a == ['ERROR: error\n']

    # Redirect to a file
    with pyscripts.redirect_stdstream(ostream=tempfile.TemporaryFile(), stream_type='b') as f:

        print('hello')
        lib.display(b'hello\n')

    f.seek(0)
    a = f.readlines()

    assert a == [b'hello\n', b'hello\n']

    # Test error raising
    with pytest.raises(ValueError):
        with pyscripts.redirect_stdstream('none'):
            pass

    with pytest.raises(ValueError):
        with pyscripts.redirect_stdstream(stream_type='n'):
            pass
