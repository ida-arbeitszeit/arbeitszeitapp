Development Setup
=================

The recommended development environment is Linux. 


Development Philosophy
-----------------------

We employ rigorous testing when developing new features for the
application or fixing bugs.  This might seem at first like a burden to 
"rapid" development, but in our experience the opposite is the case.
The extensive test coverage allows us to work on the code without the
constant fear that it might be broken because of one of our changes.

The architecture of the program is modeled after the principles of
Clean Code (Robert C. Martin, *Clean Code*, Pearson, 2008).  Here 
is a small overview of the most important
directories in the source code.

``arbeitszeit/``
    Contains the business logic of the program.  A useful heuristic for
    deciding whether your code belongs there is "Would my code still
    make sense if this app were a CLI application without a SQL
    database?"

``arbeitszeit_web/``
    Contains the code for implementing the Web interface.  The code in
    this directory should format and translate strings for display to
    the user and parse input data from forms and URLs.  This code is
    completly framework agnostic and is only concerned with engaging
    the business logic through the develivery mechanism of the World
    Wide Web.

``arbeitszeit_flask/``
    Contains the conrete implementation for persistence and IO.  We
    use the ``flask`` framework to achieve these goals.

``tests/``
   Contains all the tests.  You should find at least one test for
   every line of code in the other directories in here.


PostgreSQL Setup
-------------------

In order to work on Arbeitszeitapp you need to have the `PostgreSQL
<https://www.postgresql.org>`_ relational
database management system set up on your machine.  Once you have
PostgreSQL set up locally, you will need to create two databases.
One is a development database that you will use when running the
development server. The other database is used for the automated
test suite. The names you choose for these two databases are arbitrary 
--- e.g., ``Arbeitszeitapp_dev`` and ``Arbeitszeitapp_test``, respectively.


Virtual Environment via Nix
----------------------------

Although it is not obligatory, we encourage 
developers to use `Nix <https://nixos.org>`_, which sets up a virtual 
environment within a directory subtree, as a more powerful alternative 
to the Python `venv <https://docs.python.org/3/library/venv.html>`_ module.
A Nix flake is located in this repository.

    **A note for Mac users:**
    By default, during Nix installation, commands are added to configure path and environment
    variables within scripts located in the global /etc directory. However, macOS updates can
    overwrite these scripts, leading to Nix becoming inaccessible. To address this issue, consider
    adding the following command to your ~/.zshrc file:

        .. code-block:: bash

         # Nix
         if [ -e '/nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh' ]; then
           source '/nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh'
         fi
         # End Nix

    see https://github.com/NixOs/nix/issues/3616 for more details.

If you are working with Nix, go to the top-level directory of the repo
and enter ``nix develop`` at the command prompt.  This will cause Nix to 
read the dependency description in ``nix.flake`` and fulfill those
dependencies in a local virtual environment. You can quit the
virtual environment by typing ``exit`` at the command prompt.

Using Nix will give you the option to access a development environment with any of the supported
python versions via ``nix develop``. Check `flake.nix` for the
supported environments under the key ``devShells``. For example to
enter a development shell with ``python3.12`` set as the default
interpreter run ``nix develop .#python312``. This will drop you into a
shell with python3.12 as the default python interpreter. This won't
change anything else on your machine and the respective python
interpreter will be garbage collected the next time you run
``nix-collect-garbage``.

When working with Nix, you may add the line ``use flake`` 
at the top of an ``.envrc`` file in the top-level directory of the repo. 
When you have Direnv installed, this will automatically invoke Nix and install 
all dependencies in the virtual environment every time you enter the root code directory. 
For the line ``use flake`` to have effect you might need to install nix-direnv. 


Virtual Environment via Venv
----------------------------

If you decide to use ``venv`` instead of Nix, create a virtual environment 
with ``python -m venv venv``.
Then, to execute the virtual environment ``source ./venv/bin/activate``.
Within the venv environment, install all required packages: 
``pip install -r requirements-dev.txt``. You can deactivate the
virtual environment by typing ``deactivate`` at the command prompt.


Environment Variables
---------------------

Before you can start developing, you first have to define some
environment variables. We recommend that you define these
in an `.envrc` file in the top-level directory of the repo, and install 
`direnv <https://direnv.net/>`_ to automatically load these variables
when you enter the top-level directory of the repo.


    .. code-block:: ini

    export ARBEITSZEITAPP_CONFIGURATION_PATH=${PWD}/arbeitszeit_flask/development_settings.py
    export ARBEITSZEITAPP_SERVER_NAME=127.0.0.1:5000
    export FLASK_APP=tests.development_server:main
    export FLASK_DEBUG=1
    
    export DEV_SECRET_KEY="my_secret_key"
    export ARBEITSZEITAPP_DEV_DB="postgresql://postgres@localhost:5432/<name of dev database>"
    export ARBEITSZEITAPP_TEST_DB="postgresql://postgres@localhost:5432/<name of test database>"


Development server
------------------

When developing, you can run the development app to manually test your 
latest changes from a user interface perspective.  The app will use the
development database you set up above.  
Before you start the development server for the first time, you need to run the
database migrations via ``alembic upgrade head`` once.

Afterwards, you can start the development server with ``flask
run``.

In the development app, you might want to sign up a company or a member. While doing this,
you will be redirected to a site that asks to click a confirmation link provided in an e-mail. 
You find this invitation mail printed to ``stdout``. In general, mails are printed to ``stdout``
in the development environment. 

Moreover, when manually filing plans in the development environment, you need 
at least one accountant to approve these files. You can invite 
accountants from the terminal, using the following command:

  .. code-block:: bash

   flask invite-accountant example@mail.de

Again, an invitation mail with a confirmation link will be printed to ``stdout``.

Developers can populate the development database automatically with test data. Run

    .. code-block:: bash

     flask generate --help

to see the available options.


Code Formatting and Analysis
-----------------------------

Run ``./format_code.py`` to format Python files automatically. 
The script uses ``black`` and
``isort``.  Currently, the script applies automatic
formatting to a limited selection of paths.  You can add more paths by
adding lines to ``.autoformattingrc``.


We use type hints.  You can check the consistency of the type hints
via the ``mypy`` command. Furthermore ``flake8`` is employed to
prevent certain mistakes, such as unused imports or
uninitialized variables. Invoke both commands without arguments to
test all the eligible code.


Testing
-------

You can run the tests by executing ``pytest`` in the root folder
of this project.

You are encouraged to use the ``./run-checks`` command before you
submit changes in a pull request.  This program runs ``flake8``,
``mypy`` and the test suite.

You can generate a code coverage report at ``htmlcov/index.html`` via
the command:

.. code-block:: bash

  coverage run --source arbeitszeit_flask,arbeitszeit,arbeitszeit_web -m pytest && coverage html

It is possible to disable tests that require a PostgreSQL database to
run via an environment variable:

.. code-block:: bash

  DISABLED_TESTS="database_required" pytest

Since running tests against the database is generally very slow, we
recommend that you run only the tests for the part of the application 
on which you are working.  For example, if you are working on the business 
logic, you can use the following command to quickly run all the use case 
tests:

.. code-block:: bash

  pytest tests/use_cases

When you feel confident about your changes, and you want to run all the
tests, you can do so by executing ``./run-checks``, which will run all
tests that need to pass before your code reviewers can consider merging 
your change into the main development branch.


Update Development Dependencies
-------------------------------

We use Nix to manage the development dependencies of
``arbeitszeitapp``. We try to leverage ``nixpkgs`` as a source for our
development dependencies as much as possible, so as to reduce the required
maintenance effort. Some packages, however, are currently managed outside
of ``nixpkgs``, through custom mechanisms. The Python program
``arbeitszeit_development/update_dependencies.py`` automates this
custom package management as much as possible. You can update the
development dependencies via ``python -m
arbeitszeit_development.update_dependencies``.


Translation
-----------

We use `Flask-Babel <https://python-babel.github.io/flask-babel/>`_
for translation.

#. Add a new language:

   .. code-block::  bash

    python -m build_support.translations initialize LOCALE
    # For example for adding french
    python -m build_support.translations initialize fr


#. Add the new language to the LANGUAGES variable in
   ``arbeitszeit_flask/configuration_base.py``.

#. Mark translatable, user-facing strings in the code.

   In Python files, use the following code:

   .. code-block:: bash

    translator.gettext(message: str)
    translator.pgettext(comment: str, message: str)
    translator.ngettext(self, singular: str, plural: str, n: Number)

   In Jinja templates, use the following code:

   .. code-block:: bash

    gettext(message: str)
    ngettext(singular: str, plural: str, n)


#. Parse code for translatable strings (update ``.pot`` file):

    .. code-block:: bash

     python -m build_support.translations extract


#. Update language-specific ``.po`` files:

   .. code-block::  bash

     python -m build_support.translations update


#. Translate language-specific ``.po`` files. For translation
   programs, see `this page
   <https://www.gnu.org/software/trans-coord/manual/web-trans/html_node/PO-Editors.html>`_. 
   There is also an extension for VS Code called "gettext".


#. Compile translation files (.mo-files): This is necessary if you
   want to update the translations in your local development
   environment only. For creating build artifacts (binary and source
   distributions) this step is automatically done by the build system.

   .. code-block::  bash

    python -m build_support.translations compile


Profiling
---------

This project uses ``flask_profiler`` to provided a very basic
graphical user interface for response times.  More profiling
information is printed to ``stdout`` (the terminal) when detailed
debugging is enabled. Run the following in the same terminal as where you
start the development server to enable detailed profiling:

   .. code-block:: bash

    export DEBUG_DETAILS=true


Documentation
-------------

Run:

   .. code-block:: bash

    make clean
    make html

in the root folder of the project to generate developer documentation,
including auto-generated API docs.  Open the documentation in your
browser at ``build/html/index.html``. The HTML code is generated from
documentation files in the ``docs`` folder, using parts of the 
top-level file ``README.rst``. 

The docs are hosted on `Read the Docs <https://arbeitszeitapp.readthedocs.io/en/latest/>`_
and are automatically updated when changes are pushed to the master branch. 

Benchmarking
------------

Included in the source code for this project is a rudimentary
framework for testing the running time of our code, called
``arbeitszeit_benchmark``.  You can run all the benchmarks via
``python -m arbeitszeit_benchmark``.  This benchmarking tool can be
used to compare runtime characteristics across changes to the codebase. 
A contributor to the ``arbeitszeitapp`` might want to compare
the results of those benchmarks from the master branch to the results
from their changes. The output of this tool is in JSON.

Using a Binary Cache for Nix
----------------------------

You can access the binary cache hosted on `cachix
<https://www.cachix.org/>`_ in your development environment if you are
using Nix to manage your development environment. The binary cache
is called "arbeitszeit".  Check the `cachix docs
<https://docs.cachix.org/getting-started#using-binaries-with-nix>`_ on
how to set this up locally.  The benefit of this for you is that you
can avoid building dependencies that are already built once in the 
continuous integration (CI) pipeline.


Web API
--------

We are currently developing a JSON Web API that provides access to 
core features of Arbeitszeitapp. Its OpenAPI specification can be 
found in `/api/v1/doc/`
