Concepts
========

This document explains key concepts of the Arbeitszeitapp.


Accounts and Transactions  
-------------------------

The core principle of labor time accounting is to prevent the appropriation of others' work. Therefore, all 
transactions of working hours must be recorded, and there must be clear rules regarding which transactions 
are permitted. As proposed by the "Group of International Communists" (GIC), 
this goal is achieved through bookkeeping of transactions between accounts.  

The following accounts are necessary in labor time accounting:  

- Each company has four accounts:

  - Fixed means of production (P)
  - Liquid means of production, or raw materials (R)
  - Labor (A, "Arbeit")
  - The total product (PRD), debited at the start of each plan cycle by the sum of the P, R, and A values, and then increased back toward zero, item by item, as the finished product gets consumed.

- Each member has an account for labor certificates.

- Social accounting has a Public Sector Fund (PSF).
  
  The PSF account is used to track hours allocated to the public sector. When a member works hours, a portion of those hours (determined by the FIC, see below) is allocated to the member's account, while the remainder goes to the PSF account.

- Each cooperation has an account that tracks the differences between the cooperative price (see below) and the actual costs of the plans in the cooperation.


Plans
-----

Companies can submit plans. In these, they define a product and the planned 
production costs (in hours). 

There are productive and public plans. The products of productive plans are 
consumed in exchange for labor certificates, while the products of public 
plans can be consumed without compensation.

**Plan Approval**

When a plan is approved by an accountant, the product defined in the plan
becomes consumable. The planning company receives the planned hours for fixed
means of production, liquid means of production, and labor from the public
accounting to their P, R, and A accounts. If the plan is a productive plan,
the sum of the planned hours is also subtracted from the PRD account of the
company. If it is a public plan, no hours are subtracted from the PRD account.


Consumption
-----------

**Productive Consumption**

Productive consumption is the consumption of products by companies. Companies
cannot consume products from public plans. The consuming company specifies
whether it is acquiring fixed or liquid means of production. The cost of the
product is then subtracted from either the P or R account of the consuming
company and added to the PRD account of the producing company.

**Private Consumption**

Private consumption is the consumption by members. The cost of the product is
subtracted from the member's account and added to the PRD account of the
producing company.


**Labor Certificates and Factor of Individual Consumption (FIC)**

A company can register worked hours of its members. The respective members then
receive the number of registered hours multiplied by the current "Factor of
Individual Consumption (FIC)" on their account.

The FIC determines the part per worked hour that a member receives for private
consumption. The other part is retained to cover the costs of public plans.

The FIC is calculated as follows:

.. math::

  \text{FIC} = \frac{L-(P_o + R_o)}{L + L_o}     
  

where :math:`L` is the sum of all working hours in productive plans, 
:math:`L_o` is the sum of all working hours in public plans,
:math:`P_o` is the sum of all fixed means of production in public plans, and
:math:`R_o` is the sum of all liquid means of production in public plans. 

The FIC ranges from −∞ to 1, but in practice, it should never be negative. A negative FIC indicates that available labor is insufficient to cover the costs of public plans, leading to the issuance of negative work certificates upon work registration.

- If FIC = 0, all labor is allocated to public plans, making all goods and services freely available. When workers register hours worked, they do not receive any work certificates, since their work goes entirely to freely available public-sector goods and services and thus cannot be exchanged for private consumption.
- If FIC = 1, all labor is dedicated to productive plans, meaning nothing is freely available. Work certificates are issued in full without deductions.

Cooperations 
-------------

Companies that produce the same product can attach their plans to so-called 
"cooperations". The purpose of a cooperation is to calculate the average 
labor cost per product within a specific branch or industry. This 
average labor cost, known as the cooperative price, is what customers will 
pay for a product. It is displayed in several places in the application.

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