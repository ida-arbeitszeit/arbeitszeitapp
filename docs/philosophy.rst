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

Implementing calls to persistent storage (a.k.a the database)
=============================================================

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


  # This is a value for distinguishing between "not settings a value"
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

  # Implement a use case makes of the BookStorage protocol. This class
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
          return sum(filter(lambda _id: _id == customer_id, self.books.values()))

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
method is the standard for new implementations there is some "legacy"
code in this module.  All the production implementations are located
under ``arbeitszeit_flask.database.repositories`` and the in-memory
testing implementations can be found under
``tests.use_cases.repositories``.
