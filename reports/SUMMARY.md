# Sales analysis

Source: **REAL - UCI Online Retail II**

I kept 1,036,899 merchandise lines from 39,527 orders, worth £20,120,171. There are 5,852 identified customers. The cleaning removes cancellations, returns, non-positive prices and quantities, and non-merchandise charges.

## Products

Home Decor brought in the most revenue: **£6,092,219 (30.3%)**. Kitchen & Dining follows at £5,448,727. I assigned categories from product descriptions, and 12.6% of revenue remains in `Other`. These groups are useful for exploring the mix, but they are not an official product taxonomy.

## Customers and countries

The UK accounts for **85.7%** of revenue. The largest identified customer accounts for 3.0%; the top ten together account for 13.9%. Orders without a customer ID remain in the revenue total but cannot appear in customer rankings.

## Timing

Revenue peaks in **2011-11**, at £1,457,212 from 2,751 orders. Orders rose without revenue growth in 2010-02, 2010-05, 2011-02. Lower prices or a change in product mix could explain this, but the data has no promotion field. The final month, December 2011, ends on the 9th. These patterns come from one UK-based giftware retailer.

## What the numbers mean

Revenue is `Quantity × UnitPrice` on the retained lines, in pounds sterling. It is not profit. I would not generalize these patterns to other retailers.
