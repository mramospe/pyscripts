'''
Script to test the behaviour of the "redirect_stdstream" function.
'''

# Python
import argparse
import ctypes
import logging
import sys

# Local
import pyscripts


@pyscripts.redirecting_stdstream('stdout')
def send_to_stdout( lib ):
    '''
    Send some information to "stdout".
    '''
    print('hello')
    lib.display(b'hello\n')


@pyscripts.redirecting_stdstream('stderr')
def send_to_stderr( lib ):
    '''
    Send some information to "stderr".
    '''
    print('error', file=sys.stderr)
    lib.error(b'error\n')


@pyscripts.redirecting_stdstream('stdout')
@pyscripts.redirecting_stdstream('stderr')
def send_to_all( lib ):
    '''
    Send to both "stdout" and "stderr".
    '''
    print('hello', file=sys.stdout)
    lib.display(b'hello\n')
    print('error', file=sys.stderr)
    lib.error(b'error\n')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('library', type=str,
                        help='Path to the library')

    args = parser.parse_args()

    lib = ctypes.CDLL(args.library)

    send_to_stdout(lib)
    send_to_stderr(lib)
