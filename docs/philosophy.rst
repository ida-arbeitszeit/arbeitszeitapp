Development philosophy
======================

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
    the business logic through the develivery mechanism of the WWW.

``arbeitszeit_flask/``
    Contains the conrete implementation for persistence and IO.  We
    use the ``flask`` framework to achieve these goals.

``tests/``
   Contains all the tests.  You should find at least one test for
   every line of code in the other directories in here.
