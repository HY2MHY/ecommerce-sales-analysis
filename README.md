# Online Retail II: sales and customer analysis

I used the [UCI Online Retail II dataset](https://archive.ics.uci.edu/dataset/502/online+retail+ii) to look at three questions: what sells, where the money comes from, and when sales peak. The workbook covers one UK giftware retailer from December 2009 to December 2011. After cleaning, I kept 1,036,899 merchandise lines worth £20.12 million.

## What I found

**Home Decor brought in the most revenue:** £6.09 million, or 30.3% of the cleaned total. Kitchen & Dining was close behind at £5.45 million. I assigned categories from product descriptions, so these are working groups rather than the retailer's own product categories. The unmatched `Other` group still accounts for 12.6%.

![Revenue by product category](reports/figures/category_revenue.png)

**Sales are concentrated in the UK, but not in one customer.** The UK accounts for 85.7% of revenue. The largest identified customer accounts for 3.0%; the top ten together account for 13.9%. Orders without a customer ID count toward revenue but cannot appear in that ranking.

![Customer revenue concentration](reports/figures/customer_concentration.png)

**November 2011 was the highest-revenue month:** £1.46 million across 2,751 orders. In February 2010, May 2010, and February 2011, order counts rose while revenue fell or stayed flat. That could reflect lower prices or a different product mix; the data has no promotion field to test the cause.

![Monthly revenue and order volume](reports/figures/monthly_trends.png)

The [analysis summary](reports/SUMMARY.md) has the exact figures and caveats.

## Run it

Download `online_retail_II.xlsx` from UCI and put it at `data/raw/online_retail_II.xlsx`. The 43.5 MB workbook is not stored in Git.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make all
```

`make all` runs the tests, rebuilds the SQLite database and charts, executes the [notebook](notebooks/01_ecommerce_analysis.ipynb), and checks the reported numbers against SQL queries over the transaction table. The raw workbook is the only manual input. `make smoke` runs the pipeline on a tiny synthetic sample; its output is labeled `SYNTHETIC`.

The cleaning and category choices are in [DATA_DICTIONARY.md](DATA_DICTIONARY.md). The queries in [sql/analysis.sql](sql/analysis.sql) can also be run directly with `sqlite3 data/processed/ecommerce.db < sql/analysis.sql`.

December 2011 ends on the 9th, so I did not compare it with full months when discussing the holiday peak.

Dataset citation: Chen, D. (2012). *Online Retail II*. UCI Machine Learning Repository. https://doi.org/10.24432/C5CG6D
