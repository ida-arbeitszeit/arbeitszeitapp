Important Concepts
==================

The core principle of labor time accounting is to prevent the exploitation of others' work. 
To achieve this, all transfers of working hours must be recorded, with clear rules on what is
allowed. Based on the "Group of International Communists" (GIC), 
this goal is achieved through bookkeeping of transfers between accounts. These accounts belong
to different kind of users.

User Roles
----------

There are three user roles:

* **Companies** can file plans for each product (or service) they
  offer. A plan describes a product and defines how much working time
  it will cost.

* **Members** are workers in companies. They receive work certificates
  for their worked hours. They can use them to consume products and 
  services.

* **Accountants** are delegates of the cooperating network of
  companies. They can approve company plans based on collectively
  agreed criteria.


Accounts  
---------

The following accounts exist in the Arbeitszeitapp. See below for a 
list of allowed transfers between them.

- Each company has four accounts:

  - **p**: Fixed means of production
  - **r**: Liquid means of production
  - **a**: Labor ("Arbeit")
  - **prd**: The total product, debited at the start of each plan cycle by 
    the sum of the P, R, and A values, and then increased back toward zero, 
    item by item, as the finished product gets consumed.

- **member**: Each member has an account for labor certificates.

- **psf**: The PSF account is used to track hours credited to and debited from
  the public sector. It is used to cover the costs of public plans.

- **cooperation**: Companies can form cooperations. Each cooperation has an 
  account that tracks the differences between the consumed cooperative (averaged) prices and the 
  actual costs (see below).

Plans
-----

Companies file plans. In these, they define a product and the planned 
production costs (in hours). 

There are productive and public plans. The products of productive plans are 
consumed in exchange for labor certificates, while the products of public 
plans are consumed without compensation.

When a plan gets approved, the planning company recieves the planned hours credited 
to their P, R, and A accounts.

If the plan is a productive plan, the sum of the planned hours are debited from the PRD account of the
company. If it's a public plan, the hours are debited from the PSF account.


Consumption
-----------

Productive consumption is the consumption of products by companies. Companies
cannot consume products from public plans. The consuming company specifies
whether it is acquiring fixed or liquid means of production. The cost of the
product is then subtracted from either the P or R account of the consuming
company and added to the PRD account of the producing company.

Private consumption is the consumption by members. The cost of the product is
subtracted from the member's account and added to the PRD account of the
producing company.


Labor Certificates and Factor of Individual Consumption (FIC)
-------------------------------------------------------------

Companies are registering the worked hours of its members. The respective members then
receive the number of registered hours on their account. 

At the same time, a certain amount of certificates are subtracted from the member's account 
and added to the PSF account in order to cover the costs of public plans.

This amount is determined by the FIC. The FIC is calculated as follows:

.. math::

  \text{FIC} = \frac{L-(P_o + R_o)}{L + L_o}     
  

where :math:`L` is the sum of all working hours in productive plans, 
:math:`L_o` is the sum of all working hours in public plans,
:math:`P_o` is the sum of all fixed means of production in public plans, and
:math:`R_o` is the sum of all liquid means of production in public plans. 

The FIC ranges from −∞ to 1, but in practice, it should never be negative. 
A negative FIC indicates that available labor is insufficient to cover the costs of public plans, 
leading to the issuance of negative work certificates upon work registration.

- If FIC = 0, all labor is allocated to public plans, making all goods and services freely available. 
  When workers register hours worked, they do not receive any work certificates, since their work 
  goes entirely to freely available public-sector goods and services and thus cannot be 
  exchanged for private consumption.
- If FIC = 1, all labor is dedicated to productive plans, meaning nothing is freely available. 
  Work certificates are issued in full without deductions.

Cooperations 
-------------

Companies that produce the same product can attach their plans to so-called 
"cooperations". The purpose of a cooperation is to calculate the average 
labor cost per product within a specific branch or industry. This 
average labor cost, known as the cooperative price, is what customers will 
pay for a product.

**Cooperative Price**

The logic for calculating the cooperative price is implemented in the module 
``arbeitszeit/price_calculator.py``. The cooperative price is determined 
as the average cost per product of all plans in the cooperation. 
The formula for the cooperative price is:

.. math::

  \text{cooperative price} = \frac{1}{n} \sum_{i=1}^{n} \frac{\text{cost}_i}{\text{pieces}_i}

where :math:`\text{cost}_i` is the total cost of the :math:`i`-th plan in the
cooperation and :math:`\text{pieces}_i` is the total amount of produced pieces
of the :math:`i`-th plan. The sum runs over all :math:`n` plans in the cooperation.

Note that the cooperative price is independent of the duration of the plans.
Whether one working hour was applied in one year or in one day, 
the price will be one hour.

**Coordinators of Cooperations**

"Empty" cooperations (without any plans attached) can be created by any 
company. The company that creates a cooperation automatically becomes the 
"coordinator" of that cooperation. A coordinator has several privileges and 
duties: They can accept or deny incoming cooperation requests,
remove plans from the cooperation, or transfer the coordination role to 
another company. The history of past coordinator tenures is visible to all users.

While this implementation may seem undemocratic at first glance, it must be noted that the Arbeitszeitapp
only provides the technical front-end to diverse political processes that must happen in "real life".
The app does not prescribe the political procedures that companies and communities choose to 
elect coordinators or to define cooperations. Because every company is able to create cooperations, 
companies that are unhappy with a certain coordination can easily form a new cooperation.


Transfers of labor time
-----------------------

Transfers occur between two accounts, where the debit account is charged, 
and the credit account is credited. The table below lists the allowed 
transfers and their corresponding variable names in the code.

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
     - On private consumption, the cost of the product (the cooperative price, if applicable) is subtracted from the member's account and added to the PRD account of the producing company.
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
     - On private or productive consumption, if the selling company was more productive (produced in less time) than the average of the cooperation, the difference is subtracted from the PRD account of the selling company and added to the cooperation account.
   * - compensation_for_company
     - cooperation
     - prd
     - On private or productive consumption, if the selling company was less productive (produced in more time) than the average of the cooperation, the difference is subtracted from the cooperation account and added to the PRD account of the selling company.
   * - work_certificates
     - a
     - member
     - On registration of worked hours, the hours are subtracted from the A account of the company and added to the member's account.
   * - taxes
     - member
     - psf
     - On registration of worked hours, :math:`hours * (1 - FIC)` are subtracted from the member's account and added to the PSF account.
