|Generic badge|

.. |Generic badge| image:: https://github.com/arbeitszeit/arbeitszeitapp/actions/workflows/python-app.yml/badge.svg
   :target: https://github.com/arbeitszeit/arbeitszeitapp/actions/workflows/python-app.yml

.. contents ::

.. start-introduction-do-not-delete

Introduction
============

Theory
-----------

Companies do usually calculate with working hours internally, 
but switch to money when dealing with other agents on the market. This app 
extends collective planning and working time calculation beyond the 
company boundaries. It facilitates the creation of networks 
of cooperations that exchanges products on the basis of working time 
without the need for money. 

To make this possible, it provides a planning interface for companies and 
communities as well as a working time management for companies and workers. 
Plans can get filed and approved, products can get published and paid, 
work certificates can get transferred. 

It is the implementation of a theory (`"Arbeitszeitrechnung" 
<https://aaap.be/Pages/Transition-en-Fundamental-Principles-1930.html>`_) elaborated in 
the 1920s working class movement. 


User roles
----------

There are three user roles:

* **Companies** can file plans for each product (or service) they offer. A plan describes a product and defines how much working time it will cost. 

* **Members** are workers in companies. They receive work certificates for their worked hours. They can use them to purchase products. 

* **Accountants** are delegates of the cooperating network of companies. They can approve company plans based on collectively agreed criteria. 

.. end-introduction-do-not-delete

.. start-development-setup-do-not-delete

Development setup
=================

The preferred development environment is Linux. We encourage to use nix. A nix flake is located in this repository.  


Development philosophy
-----------------------

We employ rigorous testing when developing new features for the
application or fixing bugs.  This might seem like a burden to "rapid"
development at first but in our experience the opposite is the case.
The extensive test coverage allows us to work on the code without the
constant fear that it might be broken because of the change.

The architecture of the program is modeled after the principles of
Clean Code.  Here is a small overview of the most important
directories in the source code.

``arbeitszeit/``
    Contains the business logic of the program.  A useful heuristic to
    decide if your code should be in there is "Would my code still
    make sense if this app was a CLI application without a SQL
    database?"

``arbeitszeit_web/``
    Contains the code for implementing the web interface.  The code in
    this directory should format and translate strings for display to
    the user and parse input data from forms and urls.  This code is
    completly framework agnostic and is only concerned with engaging
    the business logic through the develivery mechanism of the `WWW`.

``arbeitszeit_flask/``
    Contains the conrete implementation for persistence and IO.  We
    use the ``flask`` framework to achieve these goals.

``tests/``
   Contains all the tests.  You should find at least one test for
   every line of code in the other directories in here.


PostgreSQL setup
-------------------

Debian: ``sudo apt install -y postgresql``

Arch: ``sudo pacman -Syu postgresql``

Installing PostgreSQL will create a user named *postgres*.
Switch to postgres user: ``sudo -iu postgres``

Initialize the database: ``initdb -D /var/lib/postgres/data``

Exit user: ``exit``

Start the postgresql service: ``systemctl postgresql.service start``

To start the service automatically at boot: ``systemctl enable postgresql.service``

Switch to postgres user: ``sudo -iu postgres``

Create database: ``createdb <name of database>``


General setup
-------------

Create a virtual environment with ``python -m venv venv``

To execute the virtual environment ``source ./venv/bin/activate``

Install all packages when not using nix: ``pip install -r requirements-dev.txt``

To run the app in development mode you first have to define some
environment variables:

    .. code-block:: bash

     export ARBEITSZEITAPP_CONFIGURATION_PATH="$PWD/arbeitszeit_flask/development_settings.py"
     export FLASK_APP=arbeitszeit_flask
     export FLASK_ENV=development
     export DEV_DATABASE_URI="postgresql://postgres@localhost:5432/<name of database>"
     export DEV_SECRET_KEY=my_secret_key
     export ARBEITSZEIT_APP_SERVER_NAME=localhost:5000

After configuring the database connection you need to run the database
migrations via ``flask db upgrade``.

Afterwards you can start the development server with ``flask run -h localhost``.

Create an user by signing up and providing the required fields.
You will be redirected to a site that asks to confirm your account creating with the link provided in your Email.
This link can be found in the commandline you ran ``flask run`` starting with *<p><a href="* until the next quotation marks.
Copy this link to your browser and your account will be activated.


Code formatting and analysis
-----------------------------

There is a script that auto formats python files.  It uses ``black`` and
``isort`` for that purpose.  Currently this script only applies auto
formatting to a limited selection of paths.  You can add more paths by
adding lines to ``.autoformattingrc``.


We use type hints.  You can check the consistency of the type hints
via the ``mypy`` command. Furthermore ``flake8`` is employed to prevent certain mistakes like
for example unused imports or uninitialized variables. Invoke both commands without 
arguments to test all the eligable code.

You can print profiling info to the terminal by setting the following
environment variable:

   .. code-block:: bash
    
    export DEBUG_DETAILS=true


Testing
-------

You can run the tests via by executing ``pytest`` in the root folder
of this project.

You are encouraged to use the ``./run-checks`` command before you
submit changes in a pull pull request.  This program runs ``flake8``,
``mypy`` and the test suite.

You can generate a code coverage report at ``htmlcov/index.html`` via
the command::

    coverage run --source arbeitszeit_flask,arbeitszeit,arbeitszeit_web -m pytest && coverage html

Translation
-----------

We use `Flask-Babel <https://python-babel.github.io/flask-babel/>`_ for translation.

#. Add a new language: 

   .. code-block::  bash 
    
    python setup.py init_catalog -l LANGUAGE_CODE

   
#. Add the new language to the LANGUAGES variable in ``arbeitszeit_flask/configuration_base.py``.

#. Mark translatable, user-facing strings in the code.

   In python files use: 

   .. code-block:: bash
    
    translator.gettext(message: str)
    translator.pgettext(comment: str, message: str)
    translator.ngettext(self, singular: str, plural: str, n: Number)
   
   In jinja templates use: 

   .. code-block:: bash

    gettext(message: str)
    ngettext(singular: str, plural: str, n)

#. Parse code for translatable strings (create .pot file): 

    .. code-block:: bash

     python setup.py extract_messages


#. Update language specific .po-files:

   .. code-block::  bash
    
     python setup.py update_catalog

#. Translate language specific .po-files.
	
#. Compile translation files:

   .. code-block::  bash

    python setup.py compile_catalog


Email configuration
-------------------

There are two email backend implementations available.  One
implementation meant for production ``flask_mail`` and the other one
meant for development that is used by default.  To choose the email
backend set the ``MAIL_BACKEND`` setting in your flask configuration
appropriately.

* ``MAIL_BACKEND = "flask_mail"`` to use the production backend
* ``MAIL_BACKEND`` is anything else to use the development backend

See the `flask mail documentation
<https://pythonhosted.org/Flask-Mail/>`_ on how to configure the
production backend.


Documentation
--------------

Run:

   .. code-block:: bash

    make html

in the root folder of the project to generate developer documentation
including auto generated API docs.  Open the documentation in your
browser at ``build/html/index.html``.

Regenerate the API docs via:

    .. code-block:: bash

     ./regenerate-api-docs

.. end-development-setup-do-not-delete

.. start-license-do-not-delete

License
=======

All source code is distributed under the conditions of the APGL.  For
the full license text see the file ``LICENSE`` contained in this
repository.

.. end-license-do-not-delete
