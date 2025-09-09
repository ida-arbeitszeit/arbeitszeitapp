Development guide
==================

Implementing Business Logic
----------------------------

The code implementing the business logic is organized by use cases. We
define a use case as an action that a user wants to perform via our
app. Typically, a use case would still make sense even if our specific
application didn't exist. For example, companies filing plans is a use
case that would be necessary regardless of whether our application
existed.

To keep our code organized, we place each use case in its own class
within a file under the ``arbeitszeit/use_cases/`` directory. Each use
case class should expose a single "public" method that adequately
describes the use case in its name. For instance, in our example, we
might name this method ``file_plan``. This method should take exactly
one argument, in addition to the implicit ``self`` argument, which we
call the *use case request*. The return value of this method is called
the *use case response*. Both the type (class) of the request and
response are specific to the use case and should be declared in the
same module as the use case.

Here's an example for reference::

  from dataclasses import dataclass
  from decimal import Decimal
  from uuid import UUID

  @dataclass
  class Request:
      company_id: UUID
      planned_hours: Decimal
      plan_duration_in_days: int

  @dataclass
  class Response:
      is_granted: bool

  class FilePlanUseCase:
      def file_plan(self, request: Request) -> Response:
          # Here, we'd implement our business logic
          # For now, let's just return a response
          response = Response(is_granted=True)
          return response

In this example, we define two data classes, ``Request`` and
``Response``, to hold the input and output data for our use
case. Then, we create a class called ``FilePlanUseCase``, which
contains a method called ``file_plan`` to handle the "file plan" use
case. Inside this method, we'd implement the specific business logic
needed for filing plans. For now, we're just returning a simple
response to demonstrate the structure.

Testing the Business Logic
--------------------------

When we modify or add to the business logic of our application, it's
crucial to create tests. These tests serve two main purposes: Firstly,
they ensure the reliability of any changes made through thorough
testing. Having tests in place safeguards us against unintentionally
introducing bugs. Secondly, the tests act as a specification that
other programmers can refer to in order to understand what a
particular use case is expected to accomplish.

To streamline the testing process, we've established a basic framework
and provided some utility classes for setting up the application
state. The following example illustrates the components that our
testing setup offers::

  from decimal import Decimal
  from parameterized import parameterized
  from arbeitszeit.use_cases import file_plan
  from tests.use_cases.base_test_case import BaseTestCase

  class FilePlanTests(BaseTestCase):
      def setUp(self) -> None:
          # The BaseTestCase parent class handles setting up the
          # dependency injection logic.
          super().setUp()
          # Here, we create an instance of the use case object that we want to test.
          self.use_case = self.injector.get(file_plan.FilePlanUseCase)

      # The next test case demonstrates a basic scenario where we use
      # a generator object to prepare the test's preconditions.
      def test_that_existing_company_can_file_a_plan(self) -> None:
          # The BaseTestCase class provides "generator" objects that
          # aid in setting up the application state before running the test.
          company = self.company_generator.create_company()
          request = file_plan.Request(
              company_id=company,
              planned_hours=Decimal(20),
              plan_duration_in_days=5,
          )
          response = self.use_case.file_plan(request)
          # Finally, we verify that the plan was successfully filed
          # by examining the response.
          assert response.is_granted

      # This example illustrates show you can create parameterized tests.
      @parameterized.expand([0, -1, -999])
      def test_that_plans_with_non_positive_durations_are_rejected(
          self, duration: int
      ) -> None:
          company = self.company_generator.create_company()
          request = file_plan.Request(
              company_id=company,
              planned_hours=Decimal(20),
              plan_duration_in_days=duration,
          )
          response = self.use_case.file_plan(request)
          assert not response.is_granted

In this example, we define the ``FilePlanTests`` class, which inherits
from ``BaseTestCase`` to leverage its setup functionality. Within this
class, we have methods to test different scenarios, ensuring that our
business logic behaves as expected under various conditions.

Implementing calls to relational database servers
-------------------------------------------------

We segregate our business logic from implementation details as much as
possible. One such implementation detail is persistent storage, which
is currently implemented by an SQL database (DB). Boundaries between the
business logic and the DB need to be established, otherwise this
segregation cannot be facilitated.

We establish these boundaries by declaring Python ``Protocol`` types
(called protocols from now on). These protocols describe what methods
can be invoked on the DB and what the result of these invocations
is. The main entry point for calls to the DB is the `DatabaseGateway`
protocol. It has two types of methods: ``create_*`` methods to persist
new data records in the DB and ``get_*`` methods that allow us to
query existing data records. The kinds of data records that DB
implementations should understand are defined in
``arbeitszeit/records.py``. These simple dataclasses defined will be
called *records*.

Object creation
...............

Methods that are supposed to create a new data record in the DB are
expected to follow some basic principles.

First of all they should be named ``create_RECORD_NAME``.  If we would
have a record called ``CouncilReport`` then the appropriate name for
the create method is ``create_council_report``.

Secondly every *create method* must return the record that was created
in the DB. In our example the return value of
``create_council_report`` would be ``-> CouncilReport``.

Thirdly the *create method* must not have any optional arguments.  For
example arguments of the form ``argument: Optional[ArgType] = None``
are not allowed. The reason for this is that optional arguments would
mean that the default value for those optional arguments would be
implementation specific, which would make it harder to ensure
consistency across different implementations.

To give a small example::

  # records.py
  @dataclass
  class CouncilReport:
      release_date: date
      total_labor_time: Decimal

  # repositories.py
  class DatabaseGateway(Protocol):
      def create_council_report(
	  self,
	  release_date: date,
	  total_labor_time: Decimal,
      ) -> CouncilReport:
	  ...

Querying
........

Obviously we want to query the records that we created. To that end we
declare *get methods* on the database gateway interface.

Those *get methods* must be named ``get_RECORD_NAMEs``. If we would
like to declare a method to query ``CouncilReport`` records from the
DB the appropriate name for the *get method* would be
``get_council_records``. Note the plural in the method name.

The return value of those *get methods* must be a subclass of
``arbeitszeit.repositories.QueryResult`` with the proper type
parameter. Those result types are also protocols. Here would be an
example for the ``CouncilReport`` record type::

  class CouncilReportResult(QueryResult[CouncilResult], Protocol):
      def released_after(self, timestamp: datetime) -> CouncilReportResult:
          ...

Instances of ``CouncilReportResult`` represent a specific selection of
all available council report rows in our database.  In our example the
``CouncilReportResult`` protocol declares one additional method,
namely ``released_after``.  As we can see in the example code, this
method returns an instance of ``CouncilReportResult``.  Instances are
required to return a new instance ``CouncilReport`` without changing
the "original" instance.  Let's look at an example::

  all_council_reports = database_gateway.get_council_reports()
  # all_council_reports represents a query that will yield all CouncilReport records
  # stored in the DB
  recent_council_reports = all_council_reports.release_after(datetime(2020, 1, 1))
  # recent_council_reports represents a query that will yield all CouncilReport records
  # with a release_date after the 1. Jan 2020.  all_council_reports remains unchanged
  # and still yields all records from DB without any filtering.

*Get methods* must not accept any explicit
arguments. Here is an example for such a *get method*::

  class DatabaseGateway(Protocol):
      def get_council_reports(self) -> CouncilReportResult:
	  ...

The ``QueryResult`` interface declares some basic functionality for
working with records from the DB.  Most importantly is the
``__iter__`` method that returns an iterator over all records
retrieved by the DB call.  If we wanted to iterate over all
``CoucilReport`` rows in our example we would write something like the
following code::

  for report in database_gateway.get_council_reports():
      print(
	  f"Report released by council on {report.release_date} "
	  "declared a total of {report.total_labor_time} hours "
	  "being worked in the economy"
      )

It is worth noting that implementations of the ``QueryResult``
interface are expected to yield the records present at the time of
iteration (e.g. when the ``__iter__`` method is called) and not when
the ``QueryResult`` object is instantiated. In our example this would
mean that in the following code the newly created ``CouncilRecord`` is
part of the iteration the for loop::

  records = database_gateway.get_council_reports()
  database_gateway.create_council_report(release_date=datetime(...), total_labour_hours=...)
  for record in records:
      # the record created two lines above will also be printed.
      print(record)

Updating
........

Sometimes it is necessary to change records stored in the DB.  We
facilitate these updates via an update protocol.  We declare an
``update`` method on ``QueryResult`` subclasses for records that we
want to change.  The update method must return an *update object*.
These objects describe what updates are supported for the selected
rows. Let's imagine an *update object* interface for our council
report record::

  class CouncilReportUpdate(Protocol):
      def set_total_labor_hours(self, total_labor_hours: Decimal) -> CouncilReportUpdate:
          ...

      def perform(self) -> int:
          ...

In our example we can see two methods being declared. The
``set_total_labor_hours`` allows us to update the respective field for
the selected ``CouncilReport`` records.  The ``perform`` method will
actually conduct the changes in the DB.  Let's look an an example::

  reports = database_gateway.get_council_reports()
  update = reports.update()
  update.set_total_labor_hours(Decimal(12)).perform()

In this example we selected all ``CouncilReport`` records from the
database.  Then we scheduled an update from this query where the
``total_labor_time`` field of each individual council report will be
set to 12.  This update is immediately performed by calling the
``perform`` method on it.  Here is the same example written as one
statement::
  
  (
      database_gateway
      .get_council_reports()
      .update()
      .set_total_labor_hours(Decimal(12))
      .perform()
  )

The production implementation of the database gateway would emit one
single UPDATE statement to the SQL database server since only the
``perform`` method at the end of the method chain will send commands
to it.


Handling transfers of labor time
---------------------------------

Transfers of labor time between accounts are at the core of the arbeitszeitapp. 
A ``Transfer`` object follows roughly this structure::

    class Transfer:
        date: datetime
        debit_account: UUID
        credit_account: UUID
        value: Decimal

You will find the ``Transfer`` object in the business logic, in ``arbeitszeit/records.py``,
as well as a database implementation in ``arbeitszeit_flask/database/models.py``.  

Apart from these Transfer objects, we have other objects that may reference 
one or more transfers. For example, there might be a ``Consumption`` object, 
that stores the fact that a consumer has consumed a product from a plan. We can 
use the ``Consumption.transfer`` field to access the amount of labor time that was 
transfered as part of that consumption::

    class Consumption:
        consumer: UUID
        plan: UUID
        transfer: UUID  # Reference to a Transfer

A common pattern in our code is to first create a Transfer object and then another object 
that references it — all within a single use case. For instance, we might see 
in a ``ConsumptionUseCase``::

    # create the Transfer object
    transfer = self.database_gateway.create_transfer(
        date=now,
        debit_account=consumer.account,
        credit_account=company.account,
        value=amount,
    )
    # create the Consumption object
    self.database_gateway.create_consumption(
        consumer=consumer,
        plan=consumption.plan,
        transfer=transfer,
    )

Following this pattern, we can be sure to have all transfers of labor time recorded in the system as
``Transfer`` records, while we can query more detailed information through 
``Consumption`` and similar objects.

Presenters
----------

One of the design approaches of the arbeitszeitapp is a separation of
business logic and presentational logic. We have previously learned
about use case classes. We have seen that the responses returned by
calling to those use case objects are pretty abstract, hence we need a
way to turn those abstract use case responses into something we can
present to the user. This presentation can take different forms,
e.g. a http response, command line output or an email. This is the job
of **presenters**.

Presenters are classes that, when instantiated are responsible for
rendering abstract use case responses into more concrete data. Each
individual presenter class is specific to the use case response it
handles and the output format that it produces. So if we need to
render the same use case response into two diferent formats there
should be 2 different presenter classes respectivly.

A presenter produces a view model object when handling use case
responses. These view model objects are simple data types instead of
proper objects. Their attributes are mostly booleans and strings which
represent concrete output shown to the user, e.g. messages that should
be displayed on a web page, the recipients of an email or a flag that
decides if a submit button should be rendered. Note that potential
strings in those view models are already localized, e.g. text is
already translated into the proper language, dates are already
formatted.

Presenters return structured data that is not serialized yet.  E.g. a
presenter that targets the web will not render proper html but only
provide the concrete content that should be rendered into html. The
view model will be passed into a view function. The corresponding view
function is then responsible for serializing the strings and booleans
from the view model into the final output format, e.g. html, an email
or text on the screen.

Let us revisit the example from the use case chapter earlier where we
looked at an example for a use case object. Our example use case
object returned a simple response object that was supposed to
represent whether a filed plan was approved or rejected.::

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

Let us imagine that the response objects returned by this use case are
supposed to be rendered into an http response containing html. If a
plan is approved (denoted by `response.is_granted == True`) we want to
show to the user an html document with white text on green
background. When a plan is rejected we want to show an html document
with black text on red background. An example presenter could like
this::

  @dataclass
  class FilePlanPresenter:
      translator: Translator

      @dataclass
      class ViewModel:
	  text_color: str
	  background_color: str
	  message_text: str

      def render_response(self, response: FilePlanUseCase.Response) -> ViewModel:
	  if response.is_granted:
	      return self.ViewModel(
		  text_color='#ffffff',
		  background_color='#00ff00',
		  message_text=self.translator.gettext(
		      'Your plan was accepted by public accounting'
		  ),
	      )
	  else:
	      return self.ViewModel(
		  text_color='#000000',
		  background_color='#ff0000',
		  message_text=self.translator.gettext(
		      'Your plan was rejected by public accounting'
		  ),
	      )

User identification
-------------------

Arbeitszeitapp knows 3 different types of users: members, companies
and accountants. Members represent individual workers, companies
represent worker organized production units, e.g. workshops, factories
or offices. Accountants keep track of all transfers and review
plans. Each of these different user types is represented by a
dedicated user account with a universally unique identifier (UUID).

The application disallows the reuse of email addresses per account
type. This means that there can only ever be one member with the email
address ``test@test.test`` but there might be a company that shares
this email address. Passwords for logging into the application
(authentication) are set for each email address, meaning that a
company with the email address ``test@test.test`` and a member with
the same email address share a password and it is not possible to set
differing passwords for these two accounts.

Subclassing unittest.TestCase
-----------------------------

When using ``unittest.TestCase`` and its subclasses we need to follow some
basic principles of object oriented programming. One such principle is
the `Liskov Substitution Principle`_ which shall be roughly described
in the following:

The LSP states any subclasses S of a class T must be at least as
useful as T. Therefore the programmer should be able to replace any
instance of class T by class S.

Since Python supports multiple inheritance this means that we must
call the ``super`` method for any method of ``unittest.TestCase`` that
we override. This includes specifically ``setUp`` and
``tearDown``. Here is an example::

  from unittest import TestCase
  from my.package import open_db_connection


  class MyTests(unittest.TestCase):
      def setUp(self) -> None:
          super().setUp()
          self.db = open_db_connection()

      def tearDown(self) -> None:
          self.db.close()
          super().tearDown()

      def test_example(self) -> None:
          ...

Note how the order of the super() call in ``setUp`` and ``tearDown``
is flipped.

HTTP Routing
------------

The ``arbeitszeitapp`` webserver processes incoming requests using
specific functions designed for different types of requests. For
example, there's a special handler for authentication requests when a
member logs in, and another for viewing a company's accounts. Each of
these request handlers corresponds to a specific use case in a
one-to-one relationship. While there may be exceptions in our
codebase, we consider them as legacy code that should be updated to
align with a one-to-one relationship between use cases and request
handlers.

We group these individual request handlers based on their
authorization requirements. For instance, request handlers that only
allow companies to access are grouped together, while those requiring
the user to be authenticated as an accountant are placed in a
different group. To organize this, we use `Flask blueprints`_, which
are structured in direct subdirectories of the ``arbeitszeit_flask``
directory in our codebase.

Request handling
----------------

A request handler manages incoming HTTP requests and generates HTTP
responses for users. Request handlers deal with all requests directed
to a specific URI path. This means that a request handler handles
different types of requests, like ``GET`` or ``POST``.

In the ``arbeitszeitapp``, request handlers fall into two categories
based on their structure: function-based and class-based. Consider
function-based handlers as outdated, and avoid using them for new
implementations. This document focuses on explaining class-based
handlers.

For a class-based request handler, you need one method for each HTTP
method to be handled. Here's an example for a handler managing
``GET``, ``POST``, and ``DELETE`` requests::

    from arbeitszeit_flask.types import Response

    class MyRequestHandler:
        def GET(self) -> Response:
            return "Hi from GET method"

        def POST(self) -> Response:
            return "Hi from POST method"

        def DELETE(self) -> Response:
            return "Hi from DELETE method"

Ensure that the return type of each method is a valid response. Check
the type definition of ``Response`` for details on valid response types.

Having methods like ``GET`` and ``POST`` in a class describes the
abilities of a request handler. Whether specific methods are allowed
for a given path depends on the routing logic. Depending on the HTTP
routing, a handler might need to accept extra arguments. For example,
consider the `URI path pattern`_ ``/member/<uuid:member_id>``. A
handler for this path must accept a ``member_id`` argument of type
``UUID`` for any of the allowed methods::

    from arbeitszeit_flask.types import Response

    class MyRequestHandler:
        def GET(self, member_id: UUID) -> Response:
            return f"Returning member info for member {member_id}"

        def POST(self, member_id: UUID) -> Response:
            return f"Updating member info for member {member_id}"

        def DELETE(self, member_id: UUID) -> Response:
            return f"Deleting member account for member {member_id}"


Date and Time Handling
-----------------------

We work internally with the UTC timezone. To this end we use timezone-aware python 
datetime objects wherever possible. We convert datetime to the required timezone 
only in the presenter layer.


Icon Templates: Integration and Usage
-----------------------------------------

The icon template directory ``arbeitszeit_flask/templates/icons``
contains Flask-based (Jinja2) HTML template icon files of form
``<icon-name>.html``. These icon files containing one HTML SVG element
must follow a simple but specific code style to ensure proper integration
within the application.

**Icon Template Format**

Each icon template file must adhere to the following structure:

1. ``<svg>``: The root element must include exactly one HTML SVG
   element with a ``viewBox`` attribute.
2. ``<path>``: Each path within the SVG element should use
   ``fill="currentColor"`` unless a different color is intended for
   specific design purposes.

**Example**

.. code:: html

   <svg viewBox="0 0 448 512">
     <path
       fill="currentColor"
       d="M438.6 105.4C451.1 117.9 451.1 138.1 4H438.6z"
     ></path>
   </svg>

1. **ViewBox Attribute**: The ``viewBox`` attribute defines the position
   and dimension of the SVG viewport. It is essential for correct rendering
   of the SVG.

   .. code:: html

      <svg viewBox="0 0 448 512"></svg>

2. **Path Elements**: Each ``<path>`` element within the SVG should use
   ``fill="currentColor"`` to inherit the current text color. This
   allows the icon color to be easily controlled via CSS.

   .. code:: html

      <path fill="currentColor" d="..."></path>

3. **Multiple Paths**: If your SVG contains multiple paths, ensure each
   path uses ``fill="currentColor"`` unless you intentionally want a
   path to have a different fill color.

**Example with Multiple Paths**

.. code:: html

   <svg viewBox="0 0 64 64">
     <path
       fill="currentColor"
       d="..."
     ></path>
     <path
       fill="currentColor"
       d="..."
     ></path>
   </svg>

**Adding Existing SVGs**

To add an existing SVG, remove all attributes from the SVG icon except
the ``viewBox`` attribute. The ``viewBox`` attribute might have
different dimensions than our examples, which is acceptable. This
ensures consistency and proper styling within the application. The Flask
app will populate the proper attributes in a later step automatically.

**Example: Before**

.. code:: html

   <svg
     xmlns="http://www.w3.org/2000/svg"
     width="0.88em"
     height="1em"
     viewBox="0 0 448 512"
   >
     <path
       fill="currentColor"
       d="..."
     ></path>
   </svg>

**After your hand-made adjustments**

.. code:: html

   <svg viewBox="0 0 448 512">
     <path
       fill="currentColor"
       d="..."
     ></path>
   </svg>

**Icon Resources**

A comprehensive collection of icon sets can be found on
`Iconify <https://icon-sets.iconify.design/>`__. This project mostly
uses icons from the FontAwesome
`solid <https://icon-sets.iconify.design/fa6-solid/>`__ and
`regular <https://icon-sets.iconify.design/fa6-regular/>`__ collections.
However, you are free to use icons from other collections as long as
they fit into the visual style.

**Best Practices**

-  **Naming Conventions**: Use meaningful names for your icon template
   files that reflect the icon’s purpose or design.
-  **File Size**: Ensure that your HTML SVG elements are small in size (your
   icon template files should not exceed 1 KB in size)

By following these guidelines, you ensure that SVG icons are displayed
correctly and consistently throughout the application.

**Usage**

Assuming your icon template file is named ``name.html`` in the icon template
directory, you can use the ``icon`` filter in Flask template file as follows:

.. code:: html

   {{ "name"|icon }}

This will include the ``name`` SVG icon in the HTML with the specified
attributes.

**Extended Usage**

If you want to extend or override SVG attributes, do the following:

.. code:: html

   {{ "name"|icon(attrs={"data-type": "toggle", "class": "foo bar baz"}) }}

**Icon Filter Implementation**

More info, concerning the ``icon`` filter implementation, can be found in
``arbeitszeit_flask/filters.py:icon_filter``.


.. _Liskov Substitution Principle: https://en.wikipedia.org/wiki/Liskov_substitution_principle
.. _flask blueprints: https://flask.palletsprojects.com/en/latest/blueprints/
.. _URI path pattern: https://flask.palletsprojects.com/en/latest/api/#url-route-registrations
