cat << 'ENDOFFILE'

\# Marketing Analytics Platform (Capstone)

\## End-to-End Data Analyst Lifecycle: From Raw Data to Executive Reporting



A complete simulated analytics function built from scratch, as if hired as

the sole data analyst at a mid-size retail company. Covers dimensional

data modeling, ETL, deep SQL, statistical/ML modeling, two BI tools, and

automated reporting -- built as a deliberate learning project, module by

module, in the order a real analyst would encounter these skills.



\## Dataset



Online Retail II (Kaggle/UCI) -- a real UK/Ireland online gift retailer's

transaction export, Dec 2009-Dec 2011, \~1.06M rows. Chosen deliberately as

a flat, un-modeled export, so the star schema had to be designed from

scratch, not handed over pre-built.



\## What's Actually In Here



\### Module 1: Data Modeling

Documented star schema design (fact\_sales + 4 dimensions), grounded in

real EDA findings -- see outputs/schema\_design.md. Key decisions: is\_return

derived from quantity (not invoice prefix, which under-counts returns by

\~15%); zero/negative-price rows excluded as internal stock adjustments,

not real sales; UK-dominant region grouping (92% of transactions).



\### Module 2: ETL Pipeline

etl/build\_warehouse.py -- a real, re-runnable, idempotent Python script

loading the star schema into PostgreSQL. Logs row counts at every stage,

includes a data quality gate that halts the load if foreign keys contain

nulls.



\### Module 3: SQL Analytics Layer

sql/ -- five analytical queries written directly against the warehouse:

cohort retention (CTEs), RFM segmentation entirely in SQL (NTILE window

function), rolling 7-day revenue average, year-over-year growth by

category (LAG()), top-5-products-per-country (RANK()).



\### Module 4: Statistical \& Predictive Layer

notebooks/04\_statistics\_predictive.ipynb -- cohort retention heatmap, CLV

analysis (median $898.92, heavily right-skewed by wholesale-scale

outliers), and a churn classification model (logistic regression,

0.81 recall on the churned class) with a documented data-leakage

avoidance decision (recency excluded from features since it defines the

label). Churn scores written back to the warehouse as

customer\_churn\_scores.



\### Module 5: Tableau Executive Dashboard

Published dashboard with parameter-driven metric switching, cross-sheet

filter actions, and KPI cards. Built by exporting a pre-joined flat file

from PostgreSQL, since Tableau Public does not support direct database

connections (a Tableau Desktop-only feature) -- documented as a real

constraint encountered and worked around, not hidden.



\### Module 6: Power BI Report (in progress)

Connected directly to PostgreSQL (unlike Tableau Public), built the full

relational data model and four DAX measures. Demonstrates Power BI's

automatic cross-filtering, a genuine UX difference from Tableau's

manual filter-action setup.



\### Module 7: Automated Reporting

reports/generate\_report.py -- generates a polished PDF executive summary

(KPIs, trend chart, category breakdown) directly from the warehouse, with

zero manual steps. Scheduled via Windows Task Scheduler for unattended

weekly runs.



\## Repo Structure



```

marketing-analytics-platform/

|-- data/

|   |-- raw/            # source files (not committed - see Setup)

|   |-- processed/      # large exports regenerated locally, not committed

|-- notebooks/

|   |-- 00\_connection\_test.ipynb

|   |-- 01\_data\_exploration.ipynb

|   |-- 02\_etl\_development.ipynb

|   |-- 04\_statistics\_predictive.ipynb

|-- etl/

|   |-- build\_warehouse.py

|-- sql/

|   |-- 01\_cohort\_retention.sql

|   |-- 02\_rfm\_segmentation.sql

|   |-- 03\_running\_totals.sql

|   |-- 04\_yoy\_growth.sql

|   |-- 05\_top\_products\_per\_country.sql

|-- reports/

|   |-- generate\_report.py

|-- outputs/

|   |-- schema\_design.md

|-- README.md

|-- requirements.txt

```



\## Reproducing This



1\. Download Online Retail II from Kaggle into data/raw/

2\. Install PostgreSQL locally, create a database named marketing\_analytics

3\. Create a .env file with DB\_HOST, DB\_PORT, DB\_NAME, DB\_USER, DB\_PASSWORD

&#x20;  (never committed -- already in .gitignore)

4\. python -m venv venv, activate it, pip install -r requirements.txt

5\. Run etl/build\_warehouse.py to build the warehouse

6\. Run the SQL queries in sql/ against the database (pgAdmin or any client)

7\. Run notebooks/04\_statistics\_predictive.ipynb for the ML layer

8\. Run reports/generate\_report.py for the automated PDF report



\## Author



Joel Bumba - github.com/jbx-p - jbx-p.github.io

ENDOFFILE

echo "---content above, paste into notepad---"

Output



\# Marketing Analytics Platform (Capstone)

\## End-to-End Data Analyst Lifecycle: From Raw Data to Executive Reporting



A complete simulated analytics function built from scratch, as if hired as

the sole data analyst at a mid-size retail company. Covers dimensional

data modeling, ETL, deep SQL, statistical/ML modeling, two BI tools, and

automated reporting -- built as a deliberate learning project, module by

module, in the order a real analyst would encounter these skills.



\## Dataset



Online Retail II (Kaggle/UCI) -- a real UK/Ireland online gift retailer's

transaction export, Dec 2009-Dec 2011, \~1.06M rows. Chosen deliberately as

a flat, un-modeled export, so the star schema had to be designed from

scratch, not handed over pre-built.



\## What's Actually In Here



\### Module 1: Data Modeling

Documented star schema design (fact\_sales + 4 dimensions), grounded in

real EDA findings -- see outputs/schema\_design.md. Key decisions: is\_return

derived from quantity (not invoice prefix, which under-counts returns by

\~15%); zero/negative-price rows excluded as internal stock adjustments,

not real sales; UK-dominant region grouping (92% of transactions).



\### Module 2: ETL Pipeline

etl/build\_warehouse.py -- a real, re-runnable, idempotent Python script

loading the star schema into PostgreSQL. Logs row counts at every stage,

includes a data quality gate that halts the load if foreign keys contain

nulls.



\### Module 3: SQL Analytics Layer

sql/ -- five analytical queries written directly against the warehouse:

cohort retention (CTEs), RFM segmentation entirely in SQL (NTILE window

function), rolling 7-day revenue average, year-over-year growth by

category (LAG()), top-5-products-per-country (RANK()).



\### Module 4: Statistical \& Predictive Layer

notebooks/04\_statistics\_predictive.ipynb -- cohort retention heatmap, CLV

analysis (median $898.92, heavily right-skewed by wholesale-scale

outliers), and a churn classification model (logistic regression,

0.81 recall on the churned class) with a documented data-leakage

avoidance decision (recency excluded from features since it defines the

label). Churn scores written back to the warehouse as

customer\_churn\_scores.



\### Module 5: Tableau Executive Dashboard

Published dashboard with parameter-driven metric switching, cross-sheet

filter actions, and KPI cards. Built by exporting a pre-joined flat file

from PostgreSQL, since Tableau Public does not support direct database

connections (a Tableau Desktop-only feature) -- documented as a real

constraint encountered and worked around, not hidden.



\### Module 6: Power BI Report (in progress)

Connected directly to PostgreSQL (unlike Tableau Public), built the full

relational data model and four DAX measures. Demonstrates Power BI's

automatic cross-filtering, a genuine UX difference from Tableau's

manual filter-action setup.



\### Module 7: Automated Reporting

reports/generate\_report.py -- generates a polished PDF executive summary

(KPIs, trend chart, category breakdown) directly from the warehouse, with

zero manual steps. Scheduled via Windows Task Scheduler for unattended

weekly runs.



\## Repo Structure



```

marketing-analytics-platform/

|-- data/

|   |-- raw/            # source files (not committed - see Setup)

|   |-- processed/      # large exports regenerated locally, not committed

|-- notebooks/

|   |-- 00\_connection\_test.ipynb

|   |-- 01\_data\_exploration.ipynb

|   |-- 02\_etl\_development.ipynb

|   |-- 04\_statistics\_predictive.ipynb

|-- etl/

|   |-- build\_warehouse.py

|-- sql/

|   |-- 01\_cohort\_retention.sql

|   |-- 02\_rfm\_segmentation.sql

|   |-- 03\_running\_totals.sql

|   |-- 04\_yoy\_growth.sql

|   |-- 05\_top\_products\_per\_country.sql

|-- reports/

|   |-- generate\_report.py

|-- outputs/

|   |-- schema\_design.md

|-- README.md

|-- requirements.txt

```



\## Reproducing This



1\. Download Online Retail II from Kaggle into data/raw/

2\. Install PostgreSQL locally, create a database named marketing\_analytics

3\. Create a .env file with DB\_HOST, DB\_PORT, DB\_NAME, DB\_USER, DB\_PASSWORD

&#x20;  (never committed -- already in .gitignore)

4\. python -m venv venv, activate it, pip install -r requirements.txt

5\. Run etl/build\_warehouse.py to build the warehouse

6\. Run the SQL queries in sql/ against the database (pgAdmin or any client)

7\. Run notebooks/04\_statistics\_predictive.ipynb for the ML layer

8\. Run reports/generate\_report.py for the automated PDF report



\## Author



Joel Bumba - github.com/jbx-p - jbx-p.github.io

\---content above, paste into notepad---

