"""Business logic"""

from project import database


class SocialAccounting:
    """A social accounting institution."""
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
            social_accounting,
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


accounting = SocialAccounting()
company = Company()
member = Member()
