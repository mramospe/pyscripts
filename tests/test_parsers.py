'''
Test functions for the "parsers" module.
'''

__author__ = ['Miguel Ramos Pernas']
__email__  = ['miguel.ramos.pernas@cern.ch']

# Python
import argparse

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

    parser = argparse.ArgumentParser(description=test_process_args.__doc__)
    parser.add_argument('--main-arg', action='store_true')

    pyscripts.define_modes(parser, [mode_1, mode_2], apply_to_parsers=add_arguments)

    return parser


def test_call():
    '''
    Test the "call" function.
    '''
    parser = _define_parser()

    args = parser.parse_args('mode_2 --test --entries 100'.split())

    assert pyscripts.call(args) == 2


def test_define_modes():
    '''
    Test the "define_modes" function.
    '''
    _define_parser()


def test_process_args():
    '''
    Test for the "parsers" module.
    '''
    parser = _define_parser()

    args = parser.parse_args('mode_1 --test --entries 100'.split())

    dct = pyscripts.process_args(args)

    assert dct['test'] == True
    assert dct['entries'] == 100
    assert dct['main_arg'] == False
    assert pyscripts.parsers.__callable_name__ not in dct

    assert getattr(args, pyscripts.parsers.__callable_name__)(**dct) == 1
