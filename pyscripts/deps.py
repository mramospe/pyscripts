'''
Define function to solve dependencies of python files on modules and
packages.
'''

__author__  = ['Miguel Ramos Pernas']
__email__   = ['miguel.ramos.pernas@cern.ch']


# Python
import functools
import importlib
import inspect
import itertools
import multiprocessing
import os

# Local
from pyscripts.display import redirect_stdstream

# Default size of the pool to get the dependencies
__pool_size__ = 4


__all__ = ['dependencies', 'direct_dependencies', 'run_once']


def dependencies( pyfile, pkg_name, abspath = False, pool_size = __pool_size__ ):
    '''
    Return the dependencies on a package for a given python file.
    Dependencies are acquired on a different process, so it does
    not interfere with this stack.
    The package must be importable from the current environment.

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
    :raises RuntimeError: If problems appear looking for dependencies.

    .. seealso:: :func:`direct_dependencies`
    '''
    parent, child = multiprocessing.Pipe()

    except_event = multiprocessing.Event()

    process = multiprocessing.Process(target=_parallelize_deps,
                                      args=(pyfile, pkg_name, True, child, except_event))

    process.start()
    deps = set(parent.recv())
    process.join()

    if except_event.is_set():
        raise RuntimeError('Problems found obtaining the dependencies for file "{}"'.format(pyfile))

    # Now get the dependencies of each of the submodules
    pool = multiprocessing.Pool(processes=pool_size)

    diff = deps
    while diff:

        bound = functools.partial(direct_dependencies,
                                  pkg_name=pkg_name, abspath=True)

        new_deps = set(itertools.chain.from_iterable(pool.map(bound, diff)))

        diff = new_deps - deps

        deps.update(diff)

    if not abspath:
        deps = _relative_deps(pyfile, deps)

    return list(deps)


def direct_dependencies( pyfile, pkg_name, abspath = False ):
    '''
    Get the direct dependencies of the given python file on a given package.
    The package must be importable from the current environment.

    :param pyfile: path to the python file to process.
    :type pyfile: str
    :param pkg_name: name of the package.
    :type pkg_name: str
    :param abspath: whether to return absolute paths.
    :param abspath: bool
    :returns: list with the paths to the dependencies.
    :rtype: list(str)

    .. seealso:: :func:`dependencies`
    '''
    deps = set()

    with redirect_stdstream():

        # Load the dependencies of the pyfile with the modules
        spec = importlib.util.spec_from_file_location("", pyfile)
        main_mod  = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_mod)

        for n, m in inspect.getmembers(main_mod):

            mod = inspect.getmodule(m)

            if mod is not None and mod.__name__.startswith(pkg_name):
                deps.add(mod.__file__)

        if not abspath:
            deps = _relative_deps(pyfile, deps)

    return list(deps)


def _parallelize_deps( pyfile, pkg_name, abspath, pipe, except_event ):
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
    :param except_event: event to be set if an error is raised while looking \
    for dependencies.
    :type except_event: multiprocessing.Event
    '''
    deps = []
    try:
        deps = direct_dependencies(pyfile, pkg_name, abspath)
    except:
        except_event.set()
    finally:
        pipe.send(deps)
        pipe.close()


def _relative_deps( pyfile, deps ):
    '''
    Calculate the path to the dependencies as a relative path from the
    python file.

    :param pyfile: path to the python file.
    :type pyfile: str
    :param deps: dependencies of the python file.
    :type deps: list(str)
    :returns: dependencies as a relative path to the python file.
    :rtype: list(str)
    '''
    pyfile_dir = os.path.dirname(os.path.abspath(pyfile))

    deps = [os.path.relpath(d, pyfile_dir) for d in deps]

    return deps


def run_once( func ):
    '''
    Decorator to make a function run only once.
    This is achieved by creating a new attribute "has_run", in the function
    wrapper.

    :param func: function to decorate.
    :type func: function
    :returns: decorated function.
    :rtype: function
    '''
    @functools.wraps(func)
    def wrapper( *args, **kwargs ):
        '''
        Wrapper around "func".
        '''
        if wrapper.has_run == False:
            wrapper.has_run = True
            return func(*args, **kwargs)

    wrapper.has_run = False

    return wrapper
