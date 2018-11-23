'''
Test functions for the "deps" module.
'''

__author__ = ['Miguel Ramos Pernas']
__email__  = ['miguel.ramos.pernas@cern.ch']

# Python
import os
import subprocess

# Local
import pyscripts

__script_path__ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts/deps.py')


def test_dependencies():
    '''
    Test the "dependencies" function.
    '''
    p = subprocess.Popen('python {} dependencies'.format(__script_path__).split())
    assert p.wait() == 0


def test_direct_dependencies():
    '''
    Test the "direct_dependencies" function.
    '''
    p = subprocess.Popen('python {} direct_dependencies'.format(__script_path__).split())
    assert p.wait() == 0


def test_run_once():
    '''
    Test function for the "run_once" decorator.
    '''
    @pyscripts.run_once
    def func():
        return 1

    # First call will return the output of the function, the second
    # will return None
    assert not func.has_run
    assert func()
    assert func.has_run
    assert not func()
