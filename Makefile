PYTHON ?= python3
DATA ?= data/raw/online_retail_II.xlsx
export MPLBACKEND := Agg
export MPLCONFIGDIR := $(CURDIR)/.matplotlib-cache
export JUPYTER_CONFIG_DIR := $(CURDIR)/.jupyter-config
export JUPYTER_DATA_DIR := $(CURDIR)/.jupyter-data
export JUPYTER_RUNTIME_DIR := $(CURDIR)/.jupyter-runtime
export IPYTHONDIR := $(CURDIR)/.ipython

.PHONY: all test analyze notebook sql-check smoke clean

all: test analyze notebook sql-check

test:
	$(PYTHON) -m pytest tests -q

analyze:
	$(PYTHON) -m src.run_analysis --data $(DATA)

notebook:
	$(PYTHON) -m jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=180 notebooks/01_ecommerce_analysis.ipynb

sql-check:
	$(PYTHON) -m src.sql_check --database data/processed/ecommerce.db --metrics reports/metrics.json

smoke:
	$(PYTHON) -m src.run_analysis --data data/raw/missing.xlsx --allow-synthetic
	$(PYTHON) -m src.sql_check --database data/processed/ecommerce.db --metrics reports/metrics.json

clean:
	rm -f data/processed/ecommerce.db reports/SUMMARY.md reports/metrics.json
	rm -f reports/figures/category_revenue.png reports/figures/customer_concentration.png reports/figures/monthly_trends.png
	find src tests -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .matplotlib-cache
	rm -rf .jupyter-config .jupyter-data .jupyter-runtime .ipython
