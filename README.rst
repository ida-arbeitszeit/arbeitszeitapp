|Generic badge|

.. |Generic badge| image:: https://github.com/arbeitszeit/arbeitszeitapp/actions/workflows/python-app.yml/badge.svg
   :target: https://github.com/arbeitszeit/arbeitszeitapp/actions/workflows/python-app.yml

.. contents ::

.. start-introduction-do-not-delete

Introduction
============

Description
------------

Arbeitszeitapp is a plattform to exchange services and products on the
basis of working time. It is designed as a Web app to be self-hosted by communities
or organizations. A test instance is running on
https://demo-app.arbeitszeitrechnung.org/.


Theory
-----------

Companies usually calculate with labour time internally, but switch to
money on the market. This app extends planning and labour time
calculation beyond the company boundaries and supports networks that
exchanges products on the basis of labour time.

It provides a planning interface for companies and communities as well
as a work time management interface for companies and workers.  Plans can get
filed and approved, products can get published, work and consumption can get registered.

This application implements a theory (`"Arbeitszeitrechnung"
<https://aaap.be/Pages/Transition-en-Fundamental-Principles-1930.html>`_)
elaborated in the 1920s by members of a German working-class movement.


User Roles
----------

There are three user roles:

* **Companies** can file plans for each product (or service) they
  offer. A plan describes a product and defines how much working time
  it will cost.

* **Members** are workers in companies. They receive work certificates
  for their worked hours. They can use them to consume products and 
  services.

* **Accountants** are delegates of the cooperating network of
  companies. They can approve company plans based on collectively
  agreed criteria.

.. end-introduction-do-not-delete

.. start-development-setup-do-not-delete

Development Setup
=================

The preferred development environment is Linux. In addition, we encourage 
developers to use `Nix <https://nixos.org>`_, which sets up a virtual 
environment within a directory subtree, as a more powerful alternative 
to the Python `venv <https://docs.python.org/3/library/venv.html>`_ module.
A Nix flake is located in this repository.


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
One is a development database that holds the data for your test 
users.  You will use this database when running the
development server as you test the application with newly developed
features or bug fixes.  The other database is used for the automated
test suite. The names you choose for these two databases are arbitrary 
--- e.g., ``Arbeitszeitapp_dev`` and ``Arbeitszeitapp_test``, respectively.


General Setup
-------------

If you are working with Nix, go to the top-level directory of the repo
and enter ``nix develop`` at the command prompt.  This will cause Nix to 
read the dependency description in ``nix.flake`` and fulfill those
dependencies in a local virtual environment.  If you are using ``venv``
instead, create a virtual environment with ``python -m venv venv``
Then, to execute the virtual environment ``source ./venv/bin/activate``.
Within the venv environment, install all required packages: 
``pip install -r requirements-dev.txt``

In order to run the app in development mode, you first have to define some
environment variables:

    .. code-block:: bash

     export ARBEITSZEITAPP_CONFIGURATION_PATH="$PWD/arbeitszeit_flask/development_settings.py"
     export FLASK_APP=arbeitszeit_flask
     export FLASK_DEBUG=1
     export DEV_DATABASE_URI="postgresql://postgres@localhost:5432/<name of database>"
     export DEV_SECRET_KEY=my_secret_key
     export ARBEITSZEIT_APP_SERVER_NAME=localhost:5000
     export ARBEITSZEITAPP_TEST_DB="postgresql://postgres@localhost:5432/<name of test database>"

You may find it useful to copy these shell commands into a script file and 
run it at the beginning of every development session.  (If you do this, be sure
to list your script in ``.gitignore`` so that it does not get committed into 
the repo.) A more pleasant alternative is to copy them into a configuration
file called ``.envrc`` in the top-level directory of the repo.  (This file name
is already included in ``.gitignore``.)  Then, you can install the `Direnv
<https://direnv.net>`_
utility program on your system --- outside of your virtual environment.  (If you
are using ``venv``, you can step out of the virtual environment with the ``deactivate``
command.  If you are using Nix and have issued the command ``nix develop``, you can
end the Nix session simply with ``exit`` or Ctl-D.) If you choose this route, be 
sure to follow the Direnv setup instructions for editing your shell configuration
script.  Once you do this, in any new shell, when you step into the top-level
directory of the repo (where ``.envrc`` resides), Direnv will automatically 
set the environment variables for you.  If you then add the line ``use flake`` 
at the top of your ``.envrc`` file, Direnv will first invoke Nix and install 
all dependencies in the virtual environment ---
automatically, every time you enter the root code directory. Note that the
first time you use Direnv, and any time you change ``.envrc``, you will need
to run the command ``direnv allow`` to enable Direnv to proceed.

    **A note for Mac users:**  You may find it convenient to place your clone
    of the Arbeitszeit application code base in an iCloud directory, so that 
    you can have access to the same files, in the same state, from various devices
    logged into the same iCloud account.  In this case, however, the value of 
    ``ARBEITSZEITAPP_CONFIGURATION_PATH`` as determined above using the ``PWD`` 
    environment variable may be incorrect. Once you have stepped into the 
    ``arbeitszeit`` directory and triggered Direnv to load the environment 
    variables, check the value of ``ARBEITSZEITAPP_CONFIGURATION_PATH``:
    
        .. code-block:: bash
    
         echo $ARBEITSZEITAPP_CONFIGURATION_PATH
    
    If the value is incorrect, you can hard-code your iCloud-based path as a workaround:
    
        .. code-block:: bash
    
         DIR=<actual_present_working_directory>
         export ARBEITSZEITAPP_CONFIGURATION_PATH="$DIR/arbeitszeit_flask/development_settings.py"

The configuration file ``development_settings.py`` sets several variables, but you
may find it convenient to get by with a smaller group of variables, whose values 
you can set in a top-level file, ``custom_settings.py``, to which you should direct
Flask by means of the value of ``ARBEITSZEITAPP_CONFIGURATION_PATH`` *instead*
of the value given above:

Here is a smaller ``.envrc`` that makes use of a ``custom_settings.py``:

    .. code-block:: bash

     use flake
     export ARBEITSZEITAPP_CONFIGURATION_PATH=$PWD/custom_settings.py
     export FLASK_APP=arbeitszeit_flask
     export FLASK_DEBUG=1
     export ARBEITSZEITAPP_TEST_DB="postgresql:///<name_of_your_test_DB>"

Then, here is a sample ``custom_settings.py``:

    .. code-block:: bash

     from arbeitszeit_flask.development_settings import *
     
     SECRET_KEY = 'somesecretkey'
     SQLALCHEMY_DATABASE_URI = 'postgresql:///<name_of_your_development_DB>'
     SERVER_NAME = "localhost:5000"

After configuring the database connection, you need to run the database
migrations via ``flask db upgrade``. It is mandatory to run this command 
once before developing for the first time.

Afterwards, you can start the development server with ``python -m flask
run -h localhost``.  Unfortunately ``flask run`` might not work due to
a bug in the ``werkzeug`` library.

Create a user by signing up and providing the required fields.  You
will be redirected to a site that asks to confirm your account
creating with the link provided in your e-mail.  This link can be found
in the command line when you run ``python -m flask run`` starting with
*<p><a href="* until the closing quotation marks.  Copy this link to your
browser, and your account will be activated.


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
the command::

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

Development Dependencies
------------------------

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


#. Parse code for translatable strings (create a ``.pot`` file):

    .. code-block:: bash

     python -m build_support.translations extract


#. Update language-specific ``.po`` files:

   .. code-block::  bash

     python -m build_support.translations update


#. Translate language-specific ``.po`` files. For translation
   programs, see `this page
   <https://www.gnu.org/software/trans-coord/manual/web-trans/html_node/PO-Editors.html>`_


#. Compile translation files (.mo-files): This is necessary if you
   want to update the translations in your local development
   environment only. For creating build artifacts (binary and source
   distributions) this step is automatically done by the build system.

   .. code-block::  bash

    python -m build_support.translations compile


E-mail Configuration
--------------------

There are two e-mail backend implementations available.  One
implementation is meant for production using ``flask_mail``.
The other one, meant for development, is used by default.  To choose the e-mail
backend, set the ``MAIL_BACKEND`` variable in your flask configuration
appropriately:

* ``MAIL_BACKEND = "flask_mail"`` to use the production backend.
* ``MAIL_BACKEND`` with any other value to use the development backend.

See the `flask mail documentation
<https://pythonhosted.org/Flask-Mail/>`_ on how to configure the
production backend.

Profiling
---------

This project uses ``flask_profiler`` to provided a very basic
graphical user interface for response times.  More in-depth profiling
information is printed to ``stdout`` (the terminal) when detailed
debugging is enabled. Run the following in the same terminal as where you
start the development server to enable detailed profiling:

   .. code-block:: bash

    export DEBUG_DETAILS=true


Documentation
-------------

Run:

   .. code-block:: bash

    make html

in the root folder of the project to generate developer documentation,
including auto-generated API docs.  Open the documentation in your
browser at ``build/html/index.html``. The HTML code is generated from
the top-level file ``README.rst``, which serves as the source of truth.

Regenerate the API docs via:

    .. code-block:: bash

     ./regenerate-api-docs

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

Using a Binary Cache
--------------------

You can access the binary cache hosted on `cachix
<https://www.cachix.org/>`_ in your development environment if you are
using Nix to manage your development environment. The binary cache
is called "arbeitszeit".  Check the `cachix docs
<https://docs.cachix.org/getting-started#using-binaries-with-nix>`_ on
how to set this up locally.  The benefit of this for you is that you
can avoid building dependencies that are already built once in the 
continuous integration (CI) pipeline.

Developing with different python versions
-----------------------------------------

You can access a development environment with any of the supported
python versions via ``nix develop``. Check `flake.nix` for the
supported environments under the key ``devShells``. For example to
enter a development shell with ``python3.11`` set as the default
interpreter run ``nix develop .#python311``. This will drop you into a
shell with python3.11 as the default python interpreter. This won't
change anything else on your machine and the respective python
interpreter will be garbage collected the next time you run
``nix-collect-garbage``.

Invite Accountants
-------------------

When manually filing plans in the development environment, you need 
at least one accountant to approve these files. You can invite 
accountants from the terminal, using the following command:

  .. code-block:: bash

   flask invite-accountant example@mail.de

An invitation mail will be printed to ``stdout`` containing an invite link.


Web API
--------

We are currently developing a JSON Web API that provides access to 
core features of Arbeitszeitapp. Its OpenAPI specification can be 
found in `/api/v1/doc/`

.. end-development-setup-do-not-delete

.. start-license-do-not-delete

License
=======

All source code is distributed under the conditions of the APGL.  For
the full license text, see the file ``LICENSE`` contained in this
repository.

.. end-license-do-not-delete
