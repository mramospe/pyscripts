'''
Script to test the behaviour of the "redirect_stdout" function.
'''

# Python
import argparse
import tempfile
import ctypes

# Local
import pyscripts


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('library', type=str,
                        help='Path to the library')

    args = parser.parse_args()

    lib = ctypes.CDLL(args.library)

    # Default redirector
    with pyscripts.stdout_redirector() as f:

        print('hello')
        lib.display(b'hello\n')

    f.seek(0)
    a = f.readlines()

    assert a == [b'hello\n', b'hello\n']

    # Redirect to a file
    with pyscripts.stdout_redirector(tempfile.TemporaryFile()) as f:

        print('hello')
        lib.display(b'hello\n')

    f.seek(0)
    a = f.readlines()

    assert a == [b'hello\n', b'hello\n']
