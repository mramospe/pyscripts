=========
pyscripts
=========

.. image:: https://img.shields.io/travis/mramospe/pyscripts.svg
   :target: https://travis-ci.org/mramospe/pyscripts

.. image:: https://img.shields.io/badge/documentation-link-blue.svg
   :target: https://mramospe.github.io/pyscripts/

.. inclusion-marker-do-not-remove

The **pyscripts** package provides tools to work with python scripts. It is
meant to help researches doing analysis, where many of their tasks translate
into python scripts running with a given configuration mode.

Main points
===========

The idea behind this package is to provide a way to execute python scripts which
make use of pakages which handle command line arguments, like
`argparse <https://docs.python.org/3/library/argparse.html>`_.
It is also suggested to use it in combination with
`snakemake <https://snakemake.readthedocs.io/en/stable/>`_,
which would allow analysts to create fully reproducible analysis.

Installation:
=============

This package is available on `PyPi <https://pypi.org/>`_, so simply type

.. code-block:: bash

   pip install pyscripts

to install the package in your current python environment.
To use the **latest development version**, clone the repository and install with `pip`:

.. code-block:: bash

   git clone https://github.com/mramospe/pyscripts.git
   pip install pyscripts
