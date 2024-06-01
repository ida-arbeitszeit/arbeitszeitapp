Data modeling
=============

The following section discusses how we model data. That way we want to
document our reasoning behind decisions for database schemas and
calculations.

Transfer of products and services
---------------------------------

Labour time calculation is supposed to account for the flow of
products and services in society. As laid out by the GIC in their book
"Fundamental principles of Communist Production and Distribution"
labour time accounting is about registering the economic activity of
society. This means that the app should generally try to register
economic activity based on actual goods and services as they happen.
Based on this assumption we should store the transfer of any work
product for what it is. If for example a company registers the
consumption of 15 tons of steel then we should write that into the
database, which models the general ledger. A priori there is no need
to store the social necessary labour to produce those 15 tons of steel
as this information can be directly gathered from the economic plan
provided by the producers of the steel. This assumes though that
economic plans that were once approved by social accounting may not
change, at least not the estimates for P, R and L as specified by the
planner.

Labour certificates
-------------------

Similarly we should store registered hours worked "as is" on the
ledger, e.g. when a company registers that a labourer worked for 10
hours in a given time then we should store this information as
such.

Labour ceritificates can be calculated from the amount of hours that
someone worked and the FIC "at that time". It is easy to know the
amount of hours that a labourer spent working since this information
is provided directly by the companies and workers. It is harder
however to know what the FIC "at that time" was.  Does it mean the FIC
at the time of registration of the work performed or is it some
average over some "reasonable" timeframe, let's say the last month? We
cannot answer those questions easily at this moment so we should
expect that this may be subject to change. That's why we should at
least record the FIC that was considered at the time when we updated
the individual account of the worker. This may happen via a reference
to a recorded FIC or by storing the concrete value of the FIC with a
given transation, the important part is that we need to make sure that
the recorded FIC that was considered cannot be changed retroactively
as this might lead to fluctuating accounts. Fluctuating or changing
accounts are undesireable behavior because individual people will make
decisions for their consumption based on their account
balance. Therefore this number should only change in a way that is
transparent for the worker, i.e. by them performing work or consuming
something.

An alternative approach to storing the FIC would be to store the
concrete amount of certificates that was handed out to the worker
directly. This approach is probably sufficient to make the account
balance for workers stable and the FIC considered can be calculated
from the ratio of labour time given and certificates received. In that
case though it is important to store the amount of work that we
derived the amount of certificates from and reference one from the
other. This is important so that we may analyse the behavior of the
app and the properties of the accounting system as a whole. The
organized work force might for example want to know how much the FIC
fluctuates over time and how concrete workers are affected by this
fluctuation based on the industry they are working in.
