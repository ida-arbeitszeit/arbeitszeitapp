Code formatting
===============

There is a script that auto formats python files.  It uses black and
isort for that purpose.  Currently this script only applies auto
formatting to a limited selection of paths.  You can add more paths by
following the instructions provided inside the script file.

Testing
=======

You can run the tests via by executing ``pytest`` in the root folder
of this project.

Caveats
=======

When you are starting from a "fresh" database the first thing that you
need to do is to open the "index" view of the application. That is
usually ``http://localhost:5000/``. The reason for that is that
currently there is some database initialization being run when the
view is rendered for the first time.

Database Migration
==================

We use Flask-Migrate for database migration. Run ``flask db migrate`` to 
autodetect changes to the models. Run ``flask db upgrade`` 
to upgrade the database. See https://flask-migrate.readthedocs.io/en/latest/ 
for more info about Flask-Migrate.