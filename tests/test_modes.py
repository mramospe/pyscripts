'''
Test functions for the "deps" module.
'''

__author__ = ['Miguel Ramos Pernas']
__email__  = ['miguel.ramos.pernas@cern.ch']


# Python
import pytest

# Local
import pyscripts


def test_mode():
    '''
    Test for the "mode" function and the "Mode" class.
    '''
    @pyscripts.mode(inputs={'file': 'test.txt'})
    def dummy_i( inputs ):
        assert inputs['file'] == 'test.txt'

    @pyscripts.mode(outputs={'file': 'test.txt'})
    def dummy_o( outputs ):
        assert outputs['file'] == 'test.txt'

    @pyscripts.mode
    def dummy_n():
        pass

    @pyscripts.mode(inputs={'ifile': 'test_i.txt'}, outputs={'ofile': 'test_o.txt'})
    def dummy_d( inputs, outputs ):
        assert inputs['ifile'] == 'test_i.txt'
        assert outputs['ofile'] == 'test_o.txt'

    # Check all the functions
    for f in (dummy_i, dummy_o, dummy_n, dummy_d):
        f()

    # Check that the output of taking arguments by key is the same as by
    # attribute
    for f in (dummy_i, dummy_d):
        f.inputs is f['inputs']

    for f in (dummy_o, dummy_d):
        f.outputs is f['outputs']

    # Check that the names remain the same
    assert dummy_i.__name__ == 'dummy_i'
    assert dummy_n.__name__ == 'dummy_n'

    # If one calls the function with an argument that will already be given
    # by "mode", an error is raised.
    with pytest.raises(ValueError):
        dummy_i(inputs=None)
