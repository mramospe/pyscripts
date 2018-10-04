'''
Test functions for the "display" module.
'''

__author__ = ['Miguel Ramos Pernas']
__email__  = ['miguel.ramos.pernas@cern.ch']

# Local
import pyscripts

# Python
import ctypes
import os
import pytest
import subprocess


def process_redirect_script( script, tmpdir ):
    '''
    Run the given script
    '''
    # Define path to the directories
    path = os.path.dirname(os.path.abspath(__file__))

    scripts_path = os.path.join(path, 'scripts')

    # Compile C code
    code_path = os.path.join(scripts_path, 'code/display.c')

    lib_path = tmpdir.join('testlib.so')

    os.system('gcc -shared -o {} -fPIC {}'.format(lib_path, code_path))

    # Define the path to the script
    script_path = os.path.join(scripts_path, script)

    # Test default stream (must use a script to do not interfere with pytest)
    p = subprocess.Popen('python {} {}'.format(script_path, lib_path).split())
    if p.wait() != 0:
        assert False


def test_redirect_stdstream( tmpdir ):
    '''
    Test for the "redirect_stdstream" function.
    '''
    process_redirect_script('redirect_stdstream.py', tmpdir)


def test_redirecting_stdstream( tmpdir ):
    '''
    Test for the "redirecting_stdstream" decorator.
    '''
    process_redirect_script('redirecting_stdstream.py', tmpdir)
