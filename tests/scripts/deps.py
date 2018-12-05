'''
Script to test the management of dependencies.
'''

# Python
import argparse
import os
import pytest
import sys

# Local
from package import mod3
import pyscripts


def dependencies():
    '''
    Execute the test for the "dependencies" function.
    '''
    deps = pyscripts.dependencies(__file__, 'package')

    match = [os.path.join('package', d)
             for d in ('mod1.py', 'mod2.py', 'mod3.py')]

    assert all(d in match for d in deps)


def direct_dependencies():
    '''
    Execute the test for the "direct_dependencies" function.
    '''
    deps = pyscripts.direct_dependencies(__file__, 'package')

    assert all(d in deps for d in ('package/mod3.py',))


def exceptions():
    '''
    Execute the test for exceptions in the "dependencies" function.
    '''
    with pytest.raises(RuntimeError):
        deps = pyscripts.dependencies('package/raises.py', 'package')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Determine dependencies')

    pyscripts.define_modes(parser, [dependencies, direct_dependencies, exceptions])

    args = parser.parse_args()

    pyscripts.call(args)
