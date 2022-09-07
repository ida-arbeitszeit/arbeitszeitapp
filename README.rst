Overview
========

Description
-----------

Arbeitszeitapp is a webapp to exchange services and products on the basis of working time.


Introduction
------------

Companies do usually calculate with working hours internally, 
but switch to money when dealing with other agents on the market. Planning and 
working time calculation ends where the cooperation ends: on the market. 

This app extends collective planning and working time calculation beyond the 
company boundaries. In other words, it facilitates the creation of networks 
of cooperations that exchanges products on the basis of working time 
without the need for money. 

To make this possible, it provides a planning interface for companies and 
communities as well as a working time management for companies and workers. 
Plans can get filed and approved, products can get published and paid, 
work certificates can get transferred. 

It is the implementation of a theory (`"Arbeitszeitrechnung" 
<https://aaap.be/Pages/Transition-en-Fundamental-Principles-1930.html>`) elaborated in 
the 1920s working class movement. 


User roles
----------

There are three user roles:

- **Companies** can file plans for each product (or service) they offer. A plan describes a product and defines how much working time it will cost. 

- **Members** are workers in companies. They receive work certificates for their worked hours. They can use them to purchase products. 

- **Accountants** are delegates of the cooperating network of companies. They can approve company plans based on collectively agreed criteria. 


Development
===========

**Install PostgreSQL**:

- Debian: ``sudo apt install -y postgresql``
- Arch: ``sudo pacman -Syu postgresql``


Installing PostgreSQL will create a user named *postgres*.
Switch to postgres user: ``sudo -iu postgres``

Initialize the database: ``initdb -D /var/lib/postgres/data``

Exit user: ``exit``

Start the postgresql service: ``systemctl postgresql.service start``

To start the service automatically at boot: ``systemctl enable postgresql.service``

Switch to postgres user: ``sudo -iu postgres``

Create database: ``createdb <name of database>``


After installing 

The preferred development environment is Linux. We encourage to use nix. 
A nix flake is located in this repository.  

Setup
-----

Create a virtual environment with ``python -m venv venv``
To execute the virtual environment ``source ./venv/bin/activate``
Install all packages when not using nix: ``pip install -r requirements-dev.txt``

To run the app in development mode you first have to define some
environment variables::

    $ export ARBEITSZEITAPP_CONFIGURATION_PATH="$PWD/arbeitszeit_flask/development_settings.py"
    $ export FLASK_APP=arbeitszeit_flask
    $ export FLASK_ENV=development
    $ export DEV_DATABASE_URI="postgresql://postgres@localhost:5432/<name of database>"
    $ export DEV_SECRET_KEY=my_secret_key
    $ export ARBEITSZEIT_APP_SERVER_NAME=localhost:5000

After configuring the database connection you need to run the database
migrations via ``flask db upgrade``.

Afterwards you can start the development server with ``flask run``.

Create an user by signing up and providing the required fields.
You will be redirected to a site that asks to confirm your account creating with the link provided in your Email.
This link can be found in the commandline you ran ``flask run`` starting with *<p><a href="* until the next quotation marks.
Copy this link to your browser and your account will be activated.


Repository layout
-----------------

We practice clean architecture and our code is organized thusly.
Business logic related code is found in the ``arbeitszeit`` folder.
presenters are located under ``arbeitszeit_web`` and the flask related
code is found in ``arbeitszeit_flask``.  Tests are stored in the ``tests``
folder. Inside the tests folder the code is organized similarly to the
root folder: business logic tests live in ``tests/use_cases``,
presenter tests can be found in ``tests/presenters`` and flask
specific code is tested under ``tests/flask_integration``.


Documentation
-------------

Run::

  $ make html

in the root folder of the project to generate developer documentation
including auto generated API docs.  Open the documentation in your
browser at ``build/html/index.html``.

Regenerate the API docs via::

  $ ./regenerate-api-docs


Code formatting
---------------

There is a script that auto formats python files.  It uses black and
isort for that purpose.  Currently this script only applies auto
formatting to a limited selection of paths.  You can add more paths by
adding lines to ".autoformattingrc".


Code analysis
-------------

We use type hints.  You can check the consistency of the type hints
via the ``mypy`` command.

Furthermore ``flake8`` is employed to prevent certain mistakes like
for example unused imports or uninitialized variables.

Invoke both commands without arguments to test all the eligable code.

You can print profiling info to the terminal by setting the following
environment variable::

    $ export DEBUG_DETAILS=true


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

In some circumstances we use ``hypothesis`` to check for edge cases.
By default ``hypothesis`` generates only 10 examples per test to keep
testing times reasonably low. However if you want to run more examples
you can configure ``hypothesis`` for "CI mode" where at least 1000
examples are run per test.  This behavior can be controlled via the
``HYPOTHESIS_PROFILE`` environment variable.::

  # this runs all hypothesis tests with at least 1000 different
  # examples
  HYPOTHESIS_PROFILE=ci pytest


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
<https://pythonhosted.org/Flask-Mail/>` on how to configure the
production backend.


Cronjob
-------

There is a command ``flask payout``. It does the following things:

- Check if plans have expired and deactivate them
- Calculate the payout factor
- Check which plans are applicable for wage payout
- Payout the wages

This command is executed every hour on the production server. 
In development mode you can run it manually in the CLI. 


Translation
-----------

We use `Flask-Babel <https://flask-babel.tkte.ch/>` for translation.

1) Add a new language:

a. Execute::

    $ python setup.py init_catalog -l LANGUAGE_CODE

b. Add the new language to the LANGUAGES variable in
   ``arbeitszeit_flask/configuration_base.py``.

2) Mark translatable, user-facing strings in the code.

In python files use: 

- ``translator.gettext(message: str)`` 
- ``translator.pgettext(comment: str, message: str)``
- ``translator.ngettext(self, singular: str, plural: str, n: Number)``

In jinja templates use: 

- ``gettext(message: str)``
- ``ngettext(singular: str, plural: str, n)``


3) Parse code and update language specific .po-files::

    $ python setup.py update_catalog

4) Translate language specific .po-files.
	
5) Compile translation files::

    $ python setup.py compile_catalog
		

License
=======

All source code is distributed under the conditions of the APGL.  For
the full license text see the file ``LICENSE`` contained in this
repository.
