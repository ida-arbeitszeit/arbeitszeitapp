Concepts
========

This document explains key concepts of the Arbeitszeitapp.

Accounts
--------

tbd.


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

The FIC ranges from 0 to 1. It is 0 when all worked hours are registered in
public plans and 1 when all worked hours are registered in productive plans.
It ensures that the costs of public plans are covered by the labor of the
members.


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