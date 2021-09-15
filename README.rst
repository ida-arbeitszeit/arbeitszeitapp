Development setup
=================

After configuring the database connection you need to run the database
migrations via ``flask db upgrade``.

Code formatting
===============

There is a script that auto formats python files.  It uses black and
isort for that purpose.  Currently this script only applies auto
formatting to a limited selection of paths.  You can add more paths by
following the instructions provided inside the script file.

Code analysis
=============

We use type hints.  You can check the consistency of the type hints
via the ``mypy`` command.

Furthermore ``flake8`` is employed to prevent certain mistakes like
for example unused imports or uninitialized variables.

Invoke both commands without arguments to test all the eligable code.

Testing
=======

You can run the tests via by executing ``pytest`` in the root folder
of this project.

You are encouraged to use the ``./run-checks`` command before you
submit changes in a pull pull request.  This program runs ``flake8``,
``mypy`` and the test suite.

Repository layout
=================

We practice clean architecture and our code is organized thusly.
Business logic related code is found in the ``arbeitszeit`` folder.
presenters are located under ``arbeitszeit_web`` and the flask related
code is found in ``project``.  Tests are stored in the ``tests``
folder. Inside the tests folder the code is organized similarly to the
root folder: business logic tests live in ``tests/use_cases``,
presenter tests can be found in ``tests/presenters`` and flask
specific code is tested under ``tests/flask_integration``.

Caveats
=======

To run the app in development mode you first have to define some environment variables::

    $ export FLASK_ENV=development
    $ export ARBEITSZEIT_APP_CONFIGURATION="$PWD/development-settings.py"
    $ export DEV_DATABASE_URI="sqlite:///$(pwd)/db.sqlite3" 
    $ export DEV_SECRET_KEY=my_secret_key

Afterwards you can start the development server with ``flask run``.
