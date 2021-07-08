"""Business logic"""

from project import database


class SocialAccounting:
    """One social accounting institution."""

    pass


class Company:
    """A company."""

    def add_new_worker(self, user_id, company_id):
        """add new workers to company."""
        database.add_new_worker_to_company(user_id, company_id)

    def buy_product(self, buyer_type, product_id, amount, purpose, buyer_id):
        ...


class Member:
    """A regular member/worker."""

    def buy_product(self, buyer_type, product_id, buyer_id):
        ...


accounting = SocialAccounting()
company = Company()
member = Member()
