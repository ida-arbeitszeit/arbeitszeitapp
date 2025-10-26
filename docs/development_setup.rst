Development Setup
=================

Quickstart
-----------

The following steps should get you quickly set up. You find more detailed instructions in the rest of this
document.

- The recommended development environment is Linux.
- Clone the repository from Github.
- Activate a virtual environment and run ``pip install -r requirements-dev.txt`` to install the dependencies.
- Set the following environment variables in the terminal:

.. code-block:: bash

  export FLASK_APP=arbeitszeit_development.development_server:main
  export ARBEITSZEITAPP_SERVER_NAME=127.0.0.1:5000
  export ARBEITSZEITAPP_CONFIGURATION_PATH=${PWD}/arbeitszeit_development/development_settings.py
  export DEV_SECRET_KEY="my_secret_key"
  export ALEMBIC_CONFIG=${PWD}/arbeitszeit_development/alembic.ini
  export ARBEITSZEITAPP_TEST_DB=sqlite:///${PWD}/arbeitszeitapp_test.db
  export ARBEITSZEITAPP_DEV_DB=sqlite:///${PWD}/arbeitszeitapp_dev.db
  export ALEMBIC_SQLALCHEMY_DATABASE_URI=${ARBEITSZEITAPP_DEV_DB}

- Run ``pytest`` to run the testsuite.
- Run ``python -m build_support.translations compile`` (only if you need translations in the development app)
- Run ``flask run --debug`` to start the development app.


Development Philosophy
-----------------------

We employ rigorous testing when developing new features for the
application or fixing bugs.  This might seem at first like a burden to 
"rapid" development, but in our experience the opposite is the case.
The extensive test coverage allows us to work on the code without the
constant fear that it might be broken because of one of our changes.

The architecture of the program is modeled after the principles of
Clean Architecture (Robert C. Martin, *Clean Architecture*, Pearson, 2018).  Here
is a small overview of the most important
directories in the source code.

``arbeitszeit/``
    Contains the business logic of the program.  A useful heuristic for
    deciding whether your code belongs there is "Would my code still
    make sense if this app were a CLI application without a SQL
    database?"
    Use case "interactors" implement the business logic. They make use of
    the "Database Gateway" interface to persist and retrieve data. "Records"
    are business-level data structures.

``arbeitszeit_web/``
    Contains the code for implementing the Web interface.  The code in
    this directory should format and translate strings for display to
    the user and parse input data from forms and URLs.  This code is
    completly framework agnostic and is only concerned with engaging
    the business logic through the develivery mechanism of the World
    Wide Web.

``arbeitszeit_db/``
    The concrete implementation for persistence. Currently we support
    Postgres databases via SQLAlchemy.

``arbeitszeit_flask/``
    Contains the conrete implementation for IO. We use the ``flask``
    framework.

``tests/``
   Contains all the tests.  You should find at least one test for
   every line of code in the other directories in here.

Here is a diagram that shows the main components of the application:

  .. image:: images/components_overview.svg
    :alt: Overview of the main components of Arbeitszeitapp
    :width: 500px


Database Setup
-----------------

We support both PostgreSQL and SQLite databases for testing, development and 
production. In testing and development, by default, two SQLite databases are 
created automatically in the project's root directory when starting tests or 
the development server. No manual setup is necessary.

You may use your own databases by setting the environment variables 
``ARBEITSZEITAPP_DEV_DB`` and/or ``ARBEITSZEITAPP_TEST_DB`` to point to 
databases of your choice. See :ref:`environment-variables` for details.


Virtual Environment via Nix
----------------------------

Although it is not obligatory, we encourage 
developers to use `Nix <https://nixos.org>`_, which sets up a virtual 
environment within a directory subtree, as a more powerful alternative 
to the Python `venv <https://docs.python.org/3/library/venv.html>`_ module.
A Nix flake is located in this repository.

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


Virtual Environment via Venv
----------------------------

If you decide to use ``venv`` instead of Nix, create a virtual environment 
with ``python -m venv venv``.
Then, to execute the virtual environment ``source ./venv/bin/activate``.
Within the venv environment, install all required packages: 
``pip install -r requirements-dev.txt``. You can deactivate the
virtual environment by typing ``deactivate`` at the command prompt.


.. _environment-variables:

Environment Variables
---------------------

Before you can start developing, you first have to define some
environment variables. We recommend that you define these
in an `.envrc` file in the top-level directory of the repo, and install 
`direnv <https://direnv.net/>`_ to automatically load these variables
when you enter the top-level directory of the repo.

Database URIs should be in the form
used by SQLAlchemy: ``dialect[+driver]://user:password@host:port/database[?options]``.
Commented out variables are optional. 

.. code-block:: bash

  export FLASK_APP=arbeitszeit_development.development_server:main
  export ARBEITSZEITAPP_SERVER_NAME=127.0.0.1:5000
  export ARBEITSZEITAPP_CONFIGURATION_PATH=${PWD}/arbeitszeit_development/development_settings.py
  export DEV_SECRET_KEY="my_secret_key"
  export ALEMBIC_CONFIG=${PWD}/arbeitszeit_development/alembic.ini
  export ARBEITSZEITAPP_TEST_DB=sqlite:///${PWD}/arbeitszeitapp_test.db
  export ARBEITSZEITAPP_DEV_DB=sqlite:///${PWD}/arbeitszeitapp_dev.db
  export ALEMBIC_SQLALCHEMY_DATABASE_URI=${ARBEITSZEITAPP_DEV_DB}
  # export ALLOWED_OVERDRAW_MEMBER=1000
  # export DEFAULT_USER_TIMEZONE="Europe/Berlin"
  # export AUTO_MIGRATE=true


Development server
------------------

You can run the arbeitszeitapp in a development environment to manually test your 
latest changes from a user interface perspective. Start the development 
server with ``flask run --debug``.

The app will use the configured development database. You can
manually upgrade or downgrade the development database using the
`alembic` command line tool. Run `alembic --help` to see the
options. The tool has been customized to always upgrade to the newest
migration version if it detects a fresh database. Moreover, if the environment
variable ``AUTO_MIGRATE`` is set to ``true``, it will always
upgrade the database automatically when you start the development server.

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

If you have chosen to use a nix environment, the command ``nix flake check`` will test
the app against both databases, several python and nixpkgs versions. This command
is run as part of our CI Tests on Github, as well.

You can run only the tests for the part of the application 
on which you are working.  For example, if you are working on the business 
logic, you can use the following command to quickly run all the interactor 
tests:

.. code-block:: bash

  pytest tests/interactors

It is possible to disable tests that require a database to
run via an environment variable:

.. code-block:: bash

  DISABLED_TESTS="database_required" pytest

You can generate a code coverage report at ``htmlcov/index.html`` via
the command:

.. code-block:: bash

  coverage run -m pytest && coverage html


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

1. Add a new language:

  .. code-block::  bash

    python -m build_support.translations initialize LOCALE
    # For example for adding french
    python -m build_support.translations initialize fr


2. Add the new language to the LANGUAGES variable in
   ``arbeitszeit_flask/configuration_base.py``.

3. Mark translatable, user-facing strings in the code.

  In Python files, use the following code:

  .. code-block:: bash

    translator.gettext(message: str)
    translator.pgettext(comment: str, message: str)
    translator.ngettext(self, singular: str, plural: str, n: Number)

  In Jinja templates, use the following code:

  .. code-block:: bash

    gettext(message: str)
    ngettext(singular: str, plural: str, n)


4. Parse code for translatable strings (update ``.pot`` file):

  .. code-block:: bash

    python -m build_support.translations extract


5. Update language-specific ``.po`` files:

  .. code-block::  bash

    python -m build_support.translations update


6. Translate language-specific ``.po`` files. For translation
   programs, see `this page
   <https://www.gnu.org/software/trans-coord/manual/web-trans/html_node/PO-Editors.html>`_. 
   There is also an extension for VS Code called "gettext".


7. Compile translation files (.mo-files): This is necessary if you
   want to update the translations in your local development
   environment only. For creating build artifacts (binary and source
   distributions) this step is automatically done by the build system.

  .. code-block::  bash

    python -m build_support.translations compile


Profiling
---------

This project uses ``flask_profiler`` to provided a very basic
graphical user interface for response times. You can access this interface
at ``/profiling`` in the development server.


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
