'''
Test functions for the "deps" module.
'''

__author__ = ['Miguel Ramos Pernas']
__email__  = ['miguel.ramos.pernas@cern.ch']


# Python
import pytest

# Local
import pyscripts


def test_extends():
    '''
    Test for the "extends" decorator.
    '''
    # Define decorated "modes"
    @pyscripts.mode( p1 = 'p1' )
    def func1( p1, other ):
        assert p1 == 'p1'

    @pyscripts.mode
    def func2( p2 ):
        pass

    @pyscripts.mode( p3 = 'p3' )
    def func3( p3 ):
        assert p3 == 'p3'

    @pyscripts.mode(inputs={'file1': 'path/to/file1.txt'})
    def func4( inputs ):
        assert 'file1' in inputs

    @pyscripts.mode(inputs={'file2': 'path/to/file2.txt'})
    def func5( inputs ):
        assert 'file2' in inputs

    @pyscripts.mode(inputs={'file2': 'path/to/file2.txt'})
    def func6( inputs ):
        assert 'file2' in inputs
        assert inputs['file2'] == 'path/to/file2.txt'

    @pyscripts.mode(inputs={'file2': 'colliding/file2.txt'})
    def func7( inputs ):
        assert 'file2' in inputs
        assert inputs['file2'] == 'colliding/file2.txt'

    # Define the main decorated mode which depends on the previous ones
    @pyscripts.mode(main_par='main')
    @pyscripts.extends([func1, func2, func3, func5, func6],
                       collision_policy={'inputs': lambda k, a, b: {**a, **b}})
    def main( p1, p3, inputs, main_par ):
        ''' This is the docstring for "main". '''
        func1(other='other')
        func2('takes nothing')

        for f in (func3, func5, func6):
            f()

        assert main_par == 'main'

    # Run the function
    main()

    # Check name and docstring of the function
    assert main.__name__ == 'main'
    assert main.__doc__  == ''' This is the docstring for "main". '''

    # Test the breaking situations
    with pytest.raises(RuntimeError):
        @pyscripts.mode(main_par='main')
        @pyscripts.extends([func5, func6, func7])
        def main2( inputs, main_par ):
            for f in (func5, func6, func7):
                f()
            assert main_par == 'main'


def test_mode():
    '''
    Test for the "mode" function and the "Mode" class.
    '''
    @pyscripts.mode(inputs={'file': 'test.txt'})
    def func_i( inputs ):
        ''' This is a mode with docstring '''
        assert inputs['file'] == 'test.txt'

    @pyscripts.mode(outputs={'file': 'test.txt'})
    def func_o( outputs ):
        assert outputs['file'] == 'test.txt'

    @pyscripts.mode
    def func_n():
        pass

    @pyscripts.mode(inputs={'ifile': 'test_i.txt'}, outputs={'ofile': 'test_o.txt'})
    def func_d( inputs, outputs ):
        assert inputs['ifile'] == 'test_i.txt'
        assert outputs['ofile'] == 'test_o.txt'

    # Check all the functions
    for f in (func_i, func_o, func_n, func_d):
        f()

    # Check that the name and docstrings change
    assert func_i.__name__ == 'func_i'
    assert func_i.__doc__  == ''' This is a mode with docstring '''

    # Check that the output of taking arguments by key is the same as by
    # attribute
    for f in (func_i, func_d):
        f.inputs is f['inputs']

    for f in (func_o, func_d):
        f.outputs is f['outputs']

    # Check that the names remain the same
    assert func_i.__name__ == 'func_i'
    assert func_n.__name__ == 'func_n'

    # If one calls the function with an argument that will already be given
    # by "mode", an error is raised.
    with pytest.raises(ValueError):
        func_i(inputs=None)
