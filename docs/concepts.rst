Important Concepts
==================

The core principle of labor time accounting is to prevent the exploitation of others' work. To achieve this, all transfers of working hours must be recorded, with clear rules on what is allowed. Based on the "Group of International Communists" (GIC), this goal is achieved through bookkeeping of transfers between accounts. These accounts belong to different kind of users.

User Roles
----------

There are three user roles:

* **Companies** can file plans for each product (or service) they offer. A plan describes a product and defines how much working time it will cost.

* **Members** are workers in companies. They receive work certificates for their worked hours. They can use them to consume products and services.

* **Accountants** are delegates of the cooperating network of companies. They can approve company plans based on collectively agreed criteria.


Accounts  
---------

Seven different account types exist in our app. See :ref:`transfers-of-labor-time` for a list of allowed transfers between the accounts.

**p**

*owner*: Company

Each company has a "p" account ("Produktionsmittel" - means of production) where transfers related to the consumption or provision of "fixed means of production" are recorded. Fixed means of production are, for example, machines or buildings that wear out gradually and do not transfer their value to the product in one planning cycle all at once.

**r**

*owner*: Company

Each company has a "r" account ("Rohstoffe" - raw materials) where transfers related to the consumption or provision of "liquid means of production" are recorded. Liquid means of production are, for example, raw materials that transfer their value to the product in one planning cycle all at once.

**a**

*owner*: Company

Each company has an "a" account ("Arbeit" - work), where inflows and outflows of work certificates are recorded.

**prd**

*owner*: Company

Each company has a "prd" account ("Produkt" - product), where quantities of planned and delivered products are recorded. When a productive plan gets approved, the total planned costs are debited from this account. As the finished product gets consumed and work certificates are spent for it, the account balance increases back toward zero, item by item.

**member**

*owner*: Member

Each member has a "member" account where inflows and outflows of work certificates are recorded. Work certificates are credited when a company registers work and debited when the member consumes a product. 

**psf**

*owner*: Social Accounting

The "psf" account (Public Sector Fund) is used to track hours credited to and debited from the public sector. In the current implementation of the app, there is one Social Accounting instance with one psf account.

**cooperation**

*owner*: Cooperation

Each cooperation has an account that tracks the differences between the cooperative (averaged) prices and the actual costs of the products (see :ref:`cooperations` for details).


Plans
-----

Companies define in plans, beside other things, the product to be produced, the planned timeframe and the planned production costs (in hours). Companies create either productive or public plans. The difference between them is that the products of productive plans are to be consumed in exchange for labor certificates, while the products of public plans are freely available.

In our app, we distinguish between plan drafts and plans: A company creates a plan draft first. From the moment it files the plan with Social Accounting, it becomes a proper plan. 

From now on, the plan has the following attributes:

* approved: bool 
* rejected: bool
* expired: bool

When a plan gets approved, a couple of transfers of labour time are happening: The planning company receives the planned hours credited to their P, R, and A accounts. If the plan is a productive plan, the planned hours are debited from the company's own PRD account, otherwise they are debited from Social Accounting's PSF account.

We consider a plan "active" when it has been approved and not yet expired. The expiration date is approval date plus planned timeframe. After expiration, consumption cannot be registered anymore on that plan.

See the "PlanDraft" and "Plan" records in ``arbeitszeit.records.py`` for details and actual implementation. To dive deeper, you could also have a look at the following use cases in ``arbeitszeit/use_cases``:

* CreatePlanDraft
* FilePlanWithAccounting
* ApprovePlanUseCase
* RejectPlanUseCase

Consumption
-----------

Productive consumption is the consumption of products by companies. Companies cannot consume products from public plans. The consuming company specifies whether it is acquiring fixed or liquid means of production. The cost of the product is then subtracted from either the P or R account of the consuming company and added to the PRD account of the producing company.

Private consumption is the consumption by members. The cost of the product is subtracted from the member's account and added to the PRD account of the producing company.


Labor Certificates and Factor of Individual Consumption (FIC)
-------------------------------------------------------------

Companies are registering the worked hours of its members. The respective members then receive the number of registered hours on their account. 

At the same time, a certain amount of certificates are subtracted from the member's account and added to the PSF account in order to cover the costs of public plans.

This amount is determined by the FIC. The FIC is calculated as follows:

.. math::

  \text{FIC} = \frac{L-(P_o + R_o)}{L + L_o}     
  

where :math:`L` is the sum of all working hours in productive plans, 
:math:`L_o` is the sum of all working hours in public plans,
:math:`P_o` is the sum of all fixed means of production in public plans, and
:math:`R_o` is the sum of all liquid means of production in public plans. 

The FIC ranges from −∞ to 1, but in practice, it should never be negative. A negative FIC indicates that available labor is insufficient to cover the costs of public plans, leading to the issuance of negative work certificates upon work registration.

* If FIC = 0, all labor is allocated to public plans, making all goods and services freely available. When workers register hours worked, they do not receive any work certificates, since their work goes entirely to freely available public-sector goods and services and thus cannot be exchanged for private consumption.
* If FIC = 1, all labor is dedicated to productive plans, meaning nothing is freely available. Work certificates are issued in full without deductions.

.. _cooperations:

Cooperations 
-------------

Companies that produce the same product can attach their plans to so-called "cooperations". These cooperations are the means whereby companies within a given industry may express their intention to cooperate, to overcome competition and to align their production. Cooperations are a first step towards such alignment by calculating an average labor cost per product. This average labor cost is also known as the cooperative price, which is equal for all cooperating plans and which is what customers will pay for a product.

The cooperative price is determined as the average cost per product of all plans in the cooperation:

.. math::

  \text{cooperative price} = \frac{1}{n} \sum_{i=1}^{n} \frac{\text{cost}_i}{\text{pieces}_i}

where :math:`\text{cost}_i` is the total cost of the :math:`i`-th plan in the cooperation and :math:`\text{pieces}_i` is the total amount of produced pieces of the :math:`i`-th plan. The sum runs over all :math:`n` plans in the cooperation.

The cooperative price thus approximates the average socially necessary cost of the product.

**Productivity and compensation transfers**

A plan in a cooperation that is less productive than the average (needs more labour time per product) is called *underproductive*; if more productive, *overproductive*. When the product of an over- or underproductive plan is consumed, the consumer spends less or more labour certificates as required for the production of the individual product. In order to track such differences, certain "compensation" transfers between companies and cooperations are recorded whenever consumption happens (see :ref:`transfers-of-labor-time`).

**Coordinators of Cooperations**

A cooperation begins its life as empty, without any plans attached to it. Companies may then freely choose to join the new cooperation. An empty cooperation can be created by any company. The company that creates a cooperation automatically becomes the "coordinator" of that cooperation. A coordinator has several privileges and duties: They can accept or deny incoming cooperation requests, remove plans from the cooperation, or transfer the coordination role to another company. The history of past coordinator tenures is visible to all users.

While this implementation may seem undemocratic at first glance, it must be noted that the Arbeitszeitapp only provides the technical front-end to diverse political processes that must happen in "real life". The app does not prescribe the political procedures that companies and communities choose to elect coordinators or to define cooperations. Because every company is able to create cooperations, companies that are unhappy with a certain coordination can easily form a new cooperation.


.. _transfers-of-labor-time:

Transfers of labor time
-----------------------

Transfers occur between two accounts, where the debit account is charged, and the credit account is credited. The table below lists the allowed transfers and their corresponding variable names in the code.

.. list-table::
   :widths: 30 20 20 60
   :header-rows: 1

   * - Variable name
     - Debit account
     - Credit account
     - Explanation
   * - credit_p
     - prd
     - p
     - On approval of a productive plan, the planned hours for fixed means of production are subtracted from the PRD account of the company and added to the P account of the company.
   * - credit_r
     - prd
     - r
     - On approval of a productive plan, the planned hours for liquid means of production are subtracted from the PRD account of the company and added to the R account of the company.
   * - credit_a
     - prd
     - a
     - On approval of a productive plan, the planned hours for labor are subtracted from the PRD account of the company and added to the A account of the company.
   * - credit_public_p
     - psf
     - p
     - On approval of a public plan, the planned hours for fixed means of production are subtracted from the PSF account and added to the P account of the company.
   * - credit_public_r
     - psf
     - r
     - On approval of a public plan, the planned hours for liquid means of production are subtracted from the PSF account and added to the R account of the company.
   * - credit_public_a
     - psf
     - a
     - On approval of a public plan, the planned hours for labor are subtracted from the PSF account and added to the A account of the company. 
   * - private_consumption
     - member
     - prd
     - On private consumption, the cost of the product (the cooperative price, if applicable) is subtracted from the consuming member's account and added to the PRD account of the producing company.
   * - productive_consumption_p
     - p
     - prd
     - On productive consumption of fixed means of production, the cost of the product (the cooperative price, if applicable) is subtracted from the P account of the consuming company and added to the PRD account of the producing company.
   * - productive_consumption_r
     - r
     - prd
     - On productive consumption of liquid means of production, the cost of the product (the cooperative price, if applicable) is subtracted from the R account of the consuming company and added to the PRD account of the producing company.
   * - compensation_for_coop
     - prd
     - cooperation
     - On private or productive consumption, if the consumed plan was overproductive, the delta between cooperative price and individual product cost is subtracted from the PRD account of the planning company and added to the cooperation account.
   * - compensation_for_company
     - cooperation
     - prd
     - On private or productive consumption, if the consumed plan was underproductive, the delta between cooperative price and individual product cost is subtracted from the cooperation account and added to the PRD account of the planning company.
   * - work_certificates
     - a
     - member
     - On registration of worked hours, the hours are subtracted from the A account of the company and added to the member's account.
   * - taxes
     - member
     - psf
     - On registration of worked hours, :math:`hours * (1 - FIC)` are subtracted from the member's account and added to the PSF account.
