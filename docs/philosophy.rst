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

Implementing Business Logic
===========================

The code implementing the business logic is organized by use cases.  A
use case is basically an action that a user wants to perform via the
software.  Usually a use case is something that would make sense even
if this specific application would not exist. An example for that
would be the filing of plans by companies. If the arbeitszeit economy
would be conducted without this application companies would still need
to file plans with public accounting.  Every use case should "live" in
its own class inside a file under the ``arbeitszeit/use_cases/``
directory. The use case should expose a single "public" method that
describes the use case adequately in its name. In our example this
would probably be the method ``file_plan``.  This method takes exactly
one argument, apart from the implicit ``self`` argument, namely a
``request`` argument. We shall call this argument the *use case
request*. The return value of this method is called the *use case
response*. The type (class) of both values is specific to the use case
and declared as an interior class of the use case.

See this example for reference::

  # We need to import the "new" annotations module so that
  # interior classes can be handled by mypy without much hassle.
  from __future__ import annotations

  from dataclasses import dataclass
  from decimal import Decimal
  from uuid import UUID

  class FilePlanUseCase:
      @dataclass
      class Request:
          company_id: UUID
	  planned_hours: Decimal
	  plan_duration_in_days: int

      @dataclass
      class Response:
          is_granted: bool

      def file_plan(self, request: Request) -> Response:
          response = business_logic(request)
	  return response
