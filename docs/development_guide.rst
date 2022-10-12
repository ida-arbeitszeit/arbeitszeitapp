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

Implementing calls to persistent storage (a.k.a the database)
--------------------------------------------------------------

We segregate our business logic from implementation details as much as
possible. One such implementation detail is persistent storage, which
is currently implemented by an SQL database (DB). Boundaries between the
business logic and the DB need to be established, otherwise this
segregation cannot be facilitated.

We establish these boundaries by declaring Python ``Protocol`` types
(called protocols from now on). These protocols should describe what
methods can be invoked on the DB and what the result of the invocation
is. The inputs and outputs of these methods must always be "simple"
data types with no explicitly defined methods.

Let's look at an example for illustration purposes.  Here is some code
that handles information about books being borrowed by customers of a
library::

  from dataclasses import dataclass
  from typing import Dict, List, Optional, Protocol, Union
  from unittest import TestCase


  # This is a value for distinguishing between "not setting a value"
  # and "setting a value to None/NIL/NULL
  class Null:
      pass


  NULL = Null()


  # Define the BookStorage Protocol. This defines the available methods
  # on our "abstract" book storage.
  class BookStorage(Protocol):
      def get_book_count_borrowed_by_customer(self, customer_id: int) -> int:
          ...

      @dataclass
      class UpdateBooksModel:
          book_ids: List[int]
          borrowed_to: Union[None, Null, int]

      def update_books(self, update: UpdateBooksModel) -> None:
          ...

Now let's look at a possible implementation of the ``BookStorage``
protocol where the data about the books is stored in an SQL database::

  # Implement the BookStorage protocol by accessing an sql database.
  # Instances of this class can be used anywhere where the BookStorage
  # protocol is required.
  class BookStorageSqlImplementation:
      def get_book_count_borrowed_by_customer(self, customer_id: int) -> int:
          return self.run_query(
              "select count(*) from books where borrowed_to = ?;", customer_id
          )

      def update_books(self, update: BookStorage.UpdateBooksModel) -> None:
          if update.borrowed_to is None:
              return
          self.run_query(
              "update books set borrowed_to = ? where id in ?",
              update.borrowed_to,
              update.book_ids,
          )

      def run_query(self, query, *args):
          # run the specified query against the database
          pass

Now let us see how another class can use the interface to implement a
use case::

  # Implement a use case that uses the BookStorage protocol. This class
  # implements the "business logic" of borrowing books from a library.
  # The customer cannot borrow any more books if they currently borrow
  # 20 other books.
  @dataclass
  class BorrowBookUseCase:
      book_storage: BookStorage

      def borrow_book(self, customer_id: int, books: List[int]) -> str:
          books_borrowed_already = self.book_storage.get_book_count_borrowed_by_customer(
              customer_id
          )
          if books_borrowed_already > 20:
              return "denied, cannot borrow any more books"
          else:
              self.book_storage.update_books(
                  update=BookStorage.UpdateBooksModel(
                      book_ids=books, borrowed_to=customer_id
                  )
              )
              return "success, books are lended to customer"

Notice how the implementation of the use case does not depend on the
concret implementation of the BookStorage but instead only on the
protocol.  This allows ``BookStorageSqlImplementation`` to change
independently from the ``BorrowBookUseCase`` and vice versa.  A side
benefit is that we can easily change the implementation of
``BookStorage`` to another one. This comes handy when writing test
code. Here is an example for how one might implement a test for the
use case without the need to create an SQL database::

  # In our test case we don't want to use the sql implementation since
  # it is "expensive" to create new tables and set up database
  # schemes. Therefore we use a BookStorage implementation that just
  # stores all the relevant information in a python dictionary.
  class UseCaseTests(TestCase):
      def setUp(self) -> None:
          self.book_storage = BookStorageTestImpl()
          self.use_case = BorrowBookUseCase(book_storage=self.book_storage)

      def test_customer_cannot_borrow_books_if_they_already_borrowed_20(self) -> None:
          customer_id = 42
          for book_id in range(20):
              self.book_storage.create_book(book_id=book_id, borrowed_to=customer_id)
          response = self.use_case.borrow_book(customer_id, books=[1, 2, 3])
          self.assertTrue(response.startswith("denied"))


  # This class implements all the methods defined in the protocol
  # BookStorage. Notice how we can define additional methods like the
  # create_book method that is not declared in the protocol.
  class BookStorageTestImpl:
      def __init__(self) -> None:
          # This dictionary stores book ids and the customer id for
          # potential customers that borrowed the specific book.
          self.books: Dict[int, Optional[int]] = dict()

      def get_book_count_borrowed_by_customer(self, customer_id: int) -> int:
          return sum(
              1 for _ in filter(lambda _id: _id == customer_id, self.books.values())
          )

      def update_books(self, update: BookStorage.UpdateBooksModel) -> None:
          if update.borrowed_to is None:
              return
          customer_id = update.book_ids
          for book in update.book_ids:
              self.books[book] = customer_id

      def create_book(self, book_id: int, borrowed_to: Optional[int]) -> None:
          self.books[book_id] = borrowed_to

The protocols that define DB access in the *arbeitszeitapp* are
located under ``arbeitszeit.repositories``. Note that while the above
method, using protocols, is the standard for new implementations there
is some "legacy" code in this module.  All the production
implementations are located under
``arbeitszeit_flask.database.repositories`` and the in-memory testing
implementations can be found under ``tests.use_cases.repositories``.


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
