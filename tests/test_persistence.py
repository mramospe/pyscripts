'''
Test functions for the "deps" module.
'''

__author__ = ['Miguel Ramos Pernas']
__email__  = ['miguel.ramos.pernas@cern.ch']


# Python
import os
import pytest
import tempfile

# Local
import pyscripts


def test_persdirarg():
    '''
    Test for the "PersDirArg" class.
    '''
    with tempfile.TemporaryDirectory() as td:

        def dummy( ppath ):
            pass

        epath = os.path.join(td, 'example')

        p1 = pyscripts.PersDirArg('ppath', epath)
        d1 = p1.append_to_kwargs(dummy, {})
        assert d1['ppath'].path == epath

        p2 = pyscripts.PersDirArg('ppath', epath, use_func_name=True)
        d2 = p2.append_to_kwargs(dummy, {})
        assert d2['ppath'].path == os.path.join(epath, dummy.__name__)

        with pytest.raises(RuntimeError):
            d3 = p2.append_to_kwargs(dummy, d2)


def test_persistencedir():
    '''
    Test for the "PersistenceDir" class.
    '''
    with tempfile.TemporaryDirectory() as td:

        d = pyscripts.PersistenceDir(td)

        assert os.path.isdir(d.path)
        assert d.join('file.txt') == os.path.join(td, 'file.txt')

        sd = d['sdir']

        assert os.path.isdir(os.path.join(d.path, 'sdir'))
        assert os.path.join(d.path, 'sdir') == sd.path

        # The path is a private attribute
        with pytest.raises(AttributeError):
            sd.path = 'new/path'


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
            assert os.path.isdir(tmpdir.path)
            assert tmpdir.path == td

            return True

        assert function.__name__ == 'function'
        assert function()

    with tempfile.TemporaryDirectory() as td:
        @pyscripts.persisting_dir(arg='tmpdir', path=td, use_func_name=True)
        def function( tmpdir ):
            '''
            Inner function to test.
            '''
            assert os.path.isdir(tmpdir.path)
            assert os.path.join(td, 'function') == tmpdir.path

            return True

        assert function.__name__ == 'function'
        assert function()


def test_persisting_dirs():
    '''
    Test for the "persisting_dirs" function.
    '''
    with tempfile.TemporaryDirectory() as td1, tempfile.TemporaryDirectory() as td2:
        @pyscripts.persisting_dirs(dirargs=[
            pyscripts.PersDirArg('tmpdir1', td1),
            pyscripts.PersDirArg('tmpdir2', td2)]
        )
        def function( tmpdir1, tmpdir2 ):
            '''
            Inner function to test.
            '''
            for pd, td in ((tmpdir1, td1), (tmpdir2, td2)):
                assert os.path.isdir(pd.path)
                assert pd.path == td

            return True

        assert function.__name__ == 'function'
        assert function()

    with tempfile.TemporaryDirectory() as td1, tempfile.TemporaryDirectory() as td2:
        @pyscripts.persisting_dirs(
            dirargs=[pyscripts.PersDirArg('tmpdir1', td1),
                     pyscripts.PersDirArg('tmpdir2', td2)],
            use_func_name=True)
        def function( tmpdir1, tmpdir2 ):
            '''
            Inner function to test.
            '''
            for pd, td in ((tmpdir1, td1), (tmpdir2, td2)):
                assert os.path.isdir(pd.path)
                assert os.path.join(td, 'function') == pd.path

            return True

        assert function.__name__ == 'function'
        assert function()
