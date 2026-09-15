# Marketing Analytics Platform (Capstone)
## End-to-End Data Analyst Lifecycle: From Raw Data to Executive Reporting

A complete simulated analytics function built from scratch, as if hired as the sole data analyst at a mid-size retail company. Covers dimensional data modeling, ETL, deep SQL, statistical/ML modeling, two BI tools, and automated reporting — built as a deliberate learning project, module by module, in the order a real analyst would encounter these skills.

## Dataset

Online Retail II (Kaggle/UCI) — a real UK/Ireland online gift retailer's transaction export, Dec 2009–Dec 2011, ~1.06M rows. Chosen deliberately as a flat, un-modeled export, so the star schema had to be designed from scratch, not handed over pre-built.

## What's Actually In Here

### Module 1: Data Modeling
Documented star schema design (fact_sales + 4 dimensions), grounded in real EDA findings — see `outputs/schema_design.md`. Key decisions: `is_return` derived from quantity (not invoice prefix, which under-counts returns by ~15%); zero/negative-price rows excluded as internal stock adjustments, not real sales; UK-dominant region grouping (92% of transactions).

### Module 2: ETL Pipeline
`etl/build_warehouse.py` — a real, re-runnable, idempotent Python script loading the star schema into PostgreSQL. Logs row counts at every stage, includes a data quality gate that halts the load if foreign keys contain nulls.

### Module 3: SQL Analytics Layer
`sql/` — five analytical queries written directly against the warehouse: cohort retention (CTEs), RFM segmentation entirely in SQL (NTILE window function), rolling 7-day revenue average, year-over-year growth by category (LAG()), top-5-products-per-country (RANK()).

### Module 4: Statistical & Predictive Layer
`notebooks/04_statistics_predictive.ipynb` — cohort retention heatmap, CLV analysis (median $898.92, heavily right-skewed by wholesale-scale outliers), and a churn classification model (logistic regression, 0.81 recall on the churned class) with a documented data-leakage avoidance decision (recency excluded from features since it defines the label). Churn scores written back to the warehouse as `customer_churn_scores`.

### Module 5: Tableau Executive Dashboard
Published dashboard with parameter-driven metric switching, cross-sheet filter actions, and KPI cards. Built by exporting a pre-joined flat file from PostgreSQL, since Tableau Public does not support direct database connections (a Tableau Desktop-only feature) — documented as a real constraint encountered and worked around, not hidden.

### Module 6: Power BI Report (in progress)
Connected directly to PostgreSQL (unlike Tableau Public), built the full relational data model and four DAX measures. Demonstrates Power BI's automatic cross-filtering, a genuine UX difference from Tableau's manual filter-action setup.

### Module 7: Automated Reporting
`reports/generate_report.py` — generates a polished PDF executive summary (KPIs, trend chart, category breakdown) directly from the warehouse, with zero manual steps. Scheduled via Windows Task Scheduler for unattended weekly runs.

### Module 9: Executive Presentation
`presentation/build_presentation.py` — a 7-slide executive deck (business question, churn finding, revenue finding, recommendation, forward-looking automation note, technical appendix), generated programmatically via python-pptx.

## Key Finding

Purchase **frequency**, not spend, is the strongest predictor of customer churn. A customer who buys small amounts often is a meaningfully safer bet than one who spends a lot but rarely — the opposite of how "high value customer" is usually framed.

## Repo Structure

```
marketing-analytics-platform/
├── data/
│   ├── raw/            # source files (not committed - see Setup)
│   └── processed/      # large exports regenerated locally, not committed
├── notebooks/
│   ├── 00_connection_test.ipynb
│   ├── 01_data_exploration.ipynb
│   ├── 02_etl_development.ipynb
│   └── 04_statistics_predictive.ipynb
├── etl/
│   └── build_warehouse.py
├── sql/
│   ├── 01_cohort_retention.sql
│   ├── 02_rfm_segmentation.sql
│   ├── 03_running_totals.sql
│   ├── 04_yoy_growth.sql
│   └── 05_top_products_per_country.sql
├── reports/
│   └── generate_report.py
├── presentation/
│   └── build_presentation.py
├── outputs/
│   └── schema_design.md
├── README.md
└── requirements.txt
```

## Reproducing This

1. Download Online Retail II from Kaggle into `data/raw/`
2. Install PostgreSQL locally, create a database named `marketing_analytics`
3. Create a `.env` file with `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` (never committed — already in `.gitignore`)
4. `python -m venv venv`, activate it, `pip install -r requirements.txt`
5. Run `etl/build_warehouse.py` to build the warehouse
6. Run the SQL queries in `sql/` against the database (pgAdmin or any client)
7. Run `notebooks/04_statistics_predictive.ipynb` for the ML layer
8. Run `reports/generate_report.py` for the automated PDF report
9. Run `presentation/build_presentation.py` for the executive deck

## Author

Joel Bumba — [github.com/jbx-p](https://github.com/jbx-p) — [jbx-p.github.io](https://jbx-p.github.io)
