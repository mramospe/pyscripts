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

    p = subprocess.Popen('python {} exceptions'.format(__script_path__).split())
    assert p.wait() == 0


def test_direct_dependencies():
    '''
    Test the "direct_dependencies" function.
    '''
    p = subprocess.Popen('python {} direct_dependencies'.format(__script_path__).split())
    assert p.wait() == 0


