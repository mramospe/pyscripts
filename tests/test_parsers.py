'''
Test functions for the "parsers" module.
'''

__author__ = ['Miguel Ramos Pernas']
__email__  = ['miguel.ramos.pernas@cern.ch']

# Python
import argparse
import pytest

# Local
import pyscripts


def _define_parser():
    '''
    Define a custom parser.
    '''
    def mode_1( main_arg, test, entries ):
        ''' Mode 1 '''
        return 1

    def mode_2( main_arg, test, entries ):
        ''' Mode 2 '''
        return 2

    def add_arguments( p ):
        ''' Add arguments to a parser '''
        p.add_argument('--test', action='store_true')
        p.add_argument('--entries', type=int)

    parser = pyscripts.ModeArgumentParser(description='Custom parser')
    parser.add_argument('--main-arg', action='store_true')

    parser.define_modes([mode_1, mode_2], apply_to_parsers=add_arguments)

    return parser


def test_callargsproxy():
    '''
    Test the "CallableNamespace" class.
    '''
    def fun( *args, **kwargs ):
        return True

    args = argparse.Namespace(a=1, b=2)

    first = pyscripts.CallArgsProxy(fun, args)
    assert first()
    second = pyscripts.CallArgsProxy(fun, args, ['--bare'])
    assert second()

    with pytest.raises(AttributeError):
        second.function = fun


def test_call():
    '''
    Test the "call" function.
    '''
    parser = _define_parser()

    callobj = parser.parse_args_with_callable('mode_2 --test --entries 100'.split())

    assert callobj() == 2


def test_call_known():
    '''
    Test the "call" function.
    '''
    parser = _define_parser()

    callobj = parser.parse_known_args_with_callable('mode_2 --test --entries 100 --other'.split())

    assert callobj.unknown_args == ['--other']

    assert callobj() == 2


def test_modeargumentparser():
    '''
    Test the "define_modes" function.
    '''
    _define_parser()


def test_modeparserproxy():
    '''
    Test the "ModeParserProxy" class.
    '''
    def fun():
        return True

    m = pyscripts.ModeParserProxy(fun, True)
    with pytest.raises(AttributeError):
        m.function = 1
