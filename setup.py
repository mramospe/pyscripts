#!/usr/bin/env python
'''
Setup script for the pyscripts package
'''

__author__ = 'Miguel Ramos Pernas'
__email__  = 'miguel.ramos.pernas@cern.ch'


# Python
import os
import textwrap
from setuptools import setup, find_packages, Extension

#
# Version of the package. Before a new release is made
# just the "version_info" must be changed. The options
# for the fourth tag are "dev", "alpha", "beta",
# "cand", "final" or "post".
#
version_info = (0, 0, 0, 'dev', 1)

tag = version_info[3]

if tag != 'final':
    if tag == 'alpha':
        frmt = '{}a{}'
    elif tag == 'beta':
        frmt = '{}b{}'
    elif tag == 'cand':
        frmt = '{}rc{}'
    elif tag == 'post':
        frmt = '{}.post{}'
    elif tag == 'dev':
        frmt = '{}.dev{}'
    else:
        raise ValueError('Unable to parse version information')

version = frmt.format('.'.join(map(str, version_info[:3])), version_info[4])


def cpython_module( directory ):
    '''
    Determine the CPython modules available on the given directory
    '''
    extensions = []
    for path, _, fnames in os.walk(directory):
        for f in filter(lambda s: s.endswith('.c'), fnames):

            full_path = os.path.join(path, f)

            ext = Extension(full_path[:-2].replace('/', '.'), [full_path])

            extensions.append(ext)

    return extensions


def create_version_file():
    '''
    Create the file version.py given the version of the package.
    '''
    version_file = open('pyscripts/version.py', 'wt')
    version_file.write(textwrap.dedent("""\
    '''
    Auto-generated module holding the version of the pyscripts package
    '''

    __version__ = "{}"
    __version_info__ = {}

    __all__ = ['__version__', '__version_info__']
    """.format(version, version_info)))
    version_file.close()


def install_requirements():
    '''
    Get the installation requirements from the "requirements.txt" file.
    '''
    reqs = []
    with open('requirements.txt') as f:
        for line  in f:
            li = line.strip()
            if not li.startswith('#'):
                reqs.append(li)
    return reqs


def setup_package():
    '''
    Do the setup of the package, parsing the input arguments.
    '''
    try:
        import numpy
    except:
        RuntimeError('Numpy not found. Please install it before setting up this package.')

    setup(

        name = 'pyscripts',

        version = version,

        description = 'Tools to work with python scripts',

        # Read the long description from the README
        long_description = open('README.rst').read(),

        # Keywords to search for the package
        keywords = 'physics hep pyscripts',

        # Find all the packages in this directory
        packages = find_packages(),

        # Requisites
        install_requires = install_requirements(),

        # Test requirements
        setup_requires = ['pytest-runner'],

        tests_require = ['pytest'],
    )

    create_version_file()


if __name__ == '__main__':
    setup_package()
