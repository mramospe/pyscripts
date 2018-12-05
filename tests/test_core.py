'''
Test functions for the "core" module.
'''

__author__ = ['Miguel Ramos Pernas']
__email__  = ['miguel.ramos.pernas@cern.ch']

# Local
import pyscripts


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
