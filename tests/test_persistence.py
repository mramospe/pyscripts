'''
Test functions for the "deps" module.
'''

__author__ = ['Miguel Ramos Pernas']
__email__  = ['miguel.ramos.pernas@cern.ch']


# Python
import os
import tempfile

# Local
import pyscripts


def test_persistencedir():
    '''
    Test for the "PersistenceDir" class.
    '''
    with tempfile.TemporaryDirectory() as td:

        d = pyscripts.PersistenceDir(td)

        assert os.path.isdir(d.path())
        assert d.join('file.txt') == os.path.join(td, 'file.txt')

        sd = d['sdir']

        assert os.path.isdir(os.path.join(d.path(), 'sdir'))
        assert os.path.join(d.path(), 'sdir') == sd.path()


def test_persisting_dir():
    '''
    Test for the "persisting_dir" function.
    '''
    with tempfile.TemporaryDirectory() as td:
        @pyscripts.persisting_dir('tmpdir', path=td)
        def function( tmpdir ):
            '''
            Inner function to test.
            '''
            assert os.path.isdir(tmpdir.path())
            assert tmpdir.path() == td

            return True

        assert function.__name__ == 'function'
        assert function()

    with tempfile.TemporaryDirectory() as td:
        @pyscripts.persisting_dir(arg='tmpdir', path=td, use_func_name=True)
        def function( tmpdir ):
            '''
            Inner function to test.
            '''
            assert os.path.isdir(tmpdir.path())
            assert os.path.join(td, 'function') == tmpdir.path()

            return True

        assert function.__name__ == 'function'
        assert function()
