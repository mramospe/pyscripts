'''
Define function to solve dependencies of python files on modules and
packages.
'''

__author__  = ['Miguel Ramos Pernas']
__email__   = ['miguel.ramos.pernas@cern.ch']


# Python
import importlib
import inspect
import itertools
import multiprocessing
import os

# Default size of the pool to get the dependencies
__pool_size__ = 4


__all__ = ['all_dependencies', 'dependencies']


def all_dependencies( pyfile, pkg_name, abspath = False, pool_size = __pool_size__ ):
    '''
    Return the dependencies on a package for a given python file.
    Dependencies are acquired on a different process, so it does
    not interfere with this stack.

    :param pyfile: path to the python file to process.
    :type pyfile: str
    :param pkg_name: name of the package.
    :type pkg_name: str
    :param abspath: whether to return absolute paths.
    :param abspath: bool
    :param pool_size: parameter to control the amount of processes \
    to create.
    :type pool_size: int
    :returns: list with the paths to the files whom the provided file \
    depends on.
    :rtype: list(str)

    .. seealso:: :func:`dependencies`
    '''
    parent, child = multiprocessing.Pipe()

    process = multiprocessing.Process(target=_para_deps,
                                      args=(pyfile, child))

    process.start()
    deps = set(parent.recv())
    process.join()

    # Now get the dependencies of each of the submodules
    pool = multiprocessing.Pool(processes=pool_size)

    diff = deps
    while diff:

        function = lambda f: dependencies(f,
                                          pkg_name=pkg_name,
                                          abspath=abspath)

        new_deps = set(itertools.chain.from_iterable(pool.map(function, diff)))

        diff = new_deps - deps

        deps.update(diff)

    if not abspath:

        pyfile_dir = os.path.dirname(os.path.abspath(pyfile))

        deps = (os.path.join('../', d.replace(
                    os.path.commonprefix([pyfile_dir, d]), '')) for d in deps)

    return list(deps)


def _para_deps( pyfile, pkg_name, abspath, pipe ):
    '''
    Function to be sent to a different process to get the dependencies of
    a python file.

    :param pyfile: python file.
    :type pyfile: str
    :param pkg_name: name of the package.
    :type pkg_name: str
    :param abspath: whether to return absolute paths.
    :param abspath: bool
    :param pipe: pipe to communicate with the parent.
    :type pipe: multiprocessing.Pipe
    '''
    deps = dependencies(pyfile, pkg_name, abspath)
    pipe.send(deps)
    pipe.close()


def dependencies( pyfile, pkg_name, abspath = False ):
    '''
    Get the direct dependencies of the given python file on a given package.

    :param pyfile: path to the python file to process.
    :type pyfile: str
    :param pkg_name: name of the package.
    :type pkg_name: str
    :param abspath: whether to return absolute paths.
    :param abspath: bool
    :returns: list with the paths to the dependencies.
    :rtype: list(str)

    .. seealso:: :func:`all_dependencies`
    '''
    deps = []

    with stdout_redirector():

        # Load the dependencies of the pyfile with the modules
        spec = importlib.util.spec_from_file_location("", pyfile)
        mod  = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        for n, m in inspect.getmembers(mod, inspect.ismodule):
            if m.__name__.startswith(pkg_name):
                deps.append(m.__file__)

    return deps
