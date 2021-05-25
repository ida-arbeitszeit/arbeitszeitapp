"""Business logic"""

from project import database


class SocialAccounting:
    """One social accounting institution, with id=1."""
    def __init__(self) -> None:
        self.id = 1
    
    def check_plan(self):
        pass

    def grant_credits_to_company(self):
        pass

    def publish_products(self):
        pass


class Company:
    """A company."""
    def add_new_worker(self, user_id, company_id):
        """add new workers to company."""
        database.add_new_worker_to_company(user_id, company_id)

    def buy_product(self, buyer_type, product_id, buyer_id):
        database.buy(buyer_type, product_id, buyer_id)

    def delete_product(self, product_id):
        """delete own product from catalog."""
        database.delete_product(product_id)

    def create_plan(
            self,
            plan_creation_date,
            planner,
            costs_p,
            costs_r,
            costs_a,
            prd_name,
            prd_unit,
            prd_amount,
            description,
            timeframe
        ):
        """create plan."""
        database.planning(
            ...
        )
        
        accounting.check_plan()
        accounting.grant_credits_to_company()
        accounting.publish_products()


class Member:
    """A regular member/worker."""
    def buy_product(self, buyer_type, product_id, buyer_id):
        database.buy(buyer_type, product_id, buyer_id)

    def withdraw(self, user_id, amount):
        """
        executes withdrawal and returns code that can be used like money.
        """
        code = database.withdraw(user_id, amount)
        return code


# create one accounting instance in economy and in database
accounting = SocialAccounting()
database.create_social_accounting_in_db()
company = Company()
member = Member()
