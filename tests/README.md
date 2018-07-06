In order to write new tests for a member of the package, please take into
account the following considerations:

 - Any new module in the package must have its own script in this directory.
   Having many files to test a single module is not allowed.

 - The name of the test must be "test_<name>" for both scripts and test
   functions, where <name> refers to the object we want to test.

 - You can write any new test script without needing to refer explicitely to
   a module.

 - Beware of the behaviour of the "pyscipts.stdout_redirector" function, which
   interferes with "pytest". If a function makes use of it, include it in a script
   and run it with "subprocess". The scripts must be placed under "scripts/".
