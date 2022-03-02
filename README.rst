Development setup
=================

After configuring the database connection you need to run the database
migrations via ``flask db upgrade``.

Code formatting
===============

There is a script that auto formats python files.  It uses black and
isort for that purpose.  Currently this script only applies auto
formatting to a limited selection of paths.  You can add more paths by
adding lines to ".autoformattingrc".

Code analysis
=============

We use type hints.  You can check the consistency of the type hints
via the ``mypy`` command.

Furthermore ``flake8`` is employed to prevent certain mistakes like
for example unused imports or uninitialized variables.

Invoke both commands without arguments to test all the eligable code.

You can print profiling info to the terminal by setting the following
environment variable::

    $ export DEBUG_DETAILS=true

Testing
=======

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


Repository layout
=================

We practice clean architecture and our code is organized thusly.
Business logic related code is found in the ``arbeitszeit`` folder.
presenters are located under ``arbeitszeit_web`` and the flask related
code is found in ``arbeitszeit_flask``.  Tests are stored in the ``tests``
folder. Inside the tests folder the code is organized similarly to the
root folder: business logic tests live in ``tests/use_cases``,
presenter tests can be found in ``tests/presenters`` and flask
specific code is tested under ``tests/flask_integration``.

Caveats
=======

To run the app in development mode you first have to define some environment variables::

    $ export FLASK_ENV=development
    $ export ARBEITSZEIT_APP_CONFIGURATION="$PWD/arbeitszeit_flask/development_settings.py"
    $ export DEV_DATABASE_URI="sqlite:///$(pwd)/db.sqlite3" 
    $ export DEV_SECRET_KEY=my_secret_key

Afterwards you can start the development server with ``flask run``.

Email configuration
===================

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
=======

There is a command ``flask payout``. It does the following things:

- Check if plans have expired and deactivate them
- Calculate the payout factor
- Check which plans are applicable for wage payout
- Payout the wages

This command is executed every hour on the production server. 
In development mode you can run it manually in the CLI. 


Translation
===========

We use `Flask-Babel <https://flask-babel.tkte.ch/>` for translation. Available languages are set in ``arbeitszeit_flask/configuration_base.py``.

You can mark translatable strings in python files with ``translator.gettext(message: str)`` and ``translator.pgettext(comment: str, message: str)``. 
In jinja templates use ``gettext(message: str)`` and ``ngettext(singular: str, plural: str, n)``.

Parse the code and create a new ``.pot``-file::

    $ pybabel extract -F babel.cfg -k lazy_gettext -o messages.pot .

Add a new language (create a ``.po``-file for that language from ``.pot``-file)::

    $ pybabel init -i messages.pot -d arbeitszeit_flask/translations -l LANGUAGE-CODE

Update all existing translation files (intelligent merge) from ``.pot``-file::

    $ pybabel update -i messages.pot -d arbeitszeit_flask/translations

Compile (create ``.mo``-files from ``.po``-files)::

    $ pybabel compile -d arbeitszeit_flask/translations

License
=======

All source code is distributed under the conditions of the APGL.  For
the full license text see the file ``LICENSE`` contained in this
repository.
