Development guide
==================

Implementing Business Logic
----------------------------

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
or offices. Accountants keep track of all transactions and review
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


Configuration of the web server
--------------------------------

The application needs to be configured to function properly. This is
done via a configuration file. When starting ``arbeitszeitapp`` it
looks for configuration files in the following locations from top to
bottom. It loads the first configuration file it finds:

* Path set in ``ARBEITSZEITAPP_CONFIGURATION_PATH`` environment variable
* ``/etc/arbeitszeitapp/arbeitszeitapp.py``

The configuration file must be a valid python script.  Configuration
options are set as variables on the top level. The following
configuration options are available

.. py:data:: AUTO_MIGRATE
   
   Upgrade the database schema if changes are detected.

   Example: ``AUTO_MIGRATE = True``

   Default: ``False``

.. py:data:: FORCE_HTTPS

   This option controls whether the application will allow unsecure
   HTTP trafic or force a redirect to an HTTPS address.

   Example: ``FORCE_HTTPS = False``

   Default: ``True``

.. py:data:: MAIL_SERVER
   
   The server name of the SMTP server used to send mails.

.. py:data:: MAIL_PORT
   
   Port of the SMTP server used to send mails.

   Default: ``25``

.. py:data:: MAIL_USERNAME
   
   The username used to log in to the ``SMPT`` server used to send
   mail.

.. py:data:: MAIL_PASSWORD
   
   The password used to log in to the ``SMPT`` server used to send
   mail.

.. py:data:: MAIL_DEFAULT_SENDER
   
   The sender address used when sending out mail.

.. py:data:: SECRET_KEY
   
   A password used for protecting agains Cross-site request forgery
   and more. Setting this option is obligatory for many security
   measures.

.. py:data:: SECURITY_PASSWORD_SALT
   
   This option is used when encrypting passwords. Don't lose it.

.. py:data:: SERVER_NAME
   
   This variable tells the application how it is addressed. This is
   important to generate links in emails it sends out.

   Example: ``SERVER_NAME = "arbeitszeitapp.cp.org"``

.. py:data:: SQLALCHEMY_DATABASE_URI
   
   The address of the database used for persistence.

   Default: ``"sqlite:////tmp/arbeitszeitapp.db"``

   Example: ``SQLALCHEMY_DATABASE_URI = "postgresql:///my_data"``

.. py:data:: ALLOWED_OVERDRAW_MEMBER
   
   This integer defines how far members can overdraw their account.

   Default: ``0``

.. py:data:: ACCEPTABLE_RELATIVE_ACCOUNT_DEVIATION
   
   This integer defines the "relative deviation" from the ideal account balance of zero
   that is still deemed acceptable, expressed in percent and calculated 
   relative to the expected transaction value of this account.

   Example: Company XY has an absolute deviation of minus 1000 hours on its account for means
   of production (PRD account). Because it has filed plans with total costs for means of 
   production of 10000 hours (=the sum of expected transaction value), 
   its relative deviation is 10%.

   Unacceptable high deviations might get labeled as such or highlighted by the application.

   Default: ``33``


.. _Liskov Substitution Principle: https://en.wikipedia.org/wiki/Liskov_substitution_principle
