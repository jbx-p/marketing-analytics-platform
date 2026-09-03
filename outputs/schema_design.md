# Star Schema Design: Marketing Analytics Platform

## Grain Decision

fact_sales grain: one row per invoice line item, representing a REAL
customer transaction event. This explicitly EXCLUDES internal stock
adjustment/write-off entries (see Data Quality Findings below), since
those are not sales events and would violate this grain if included.

## Data Quality Findings That Shaped This Design

- 22.8% of rows (243,007 of 1,067,371) have no Customer ID. Too large to
  drop. Handled via an explicit "Unknown Customer" placeholder row in
  dim_customer (customer_key = -1), rather than excluding these rows or
  allowing nulls in the fact table's foreign key.

- Invoice-prefix-based cancellation flagging under-counts real returns:
  19,493 of 19,494 "C"-prefixed invoices have negative quantity (near-
  perfect alignment), but 3,457 additional negative-quantity rows exist
  that are NOT "C"-prefixed. Decision: is_return is derived from
  Quantity < 0 directly, not the Invoice prefix, since it captures the
  full picture of returns.

- 6,207 rows have zero or negative price, with descriptions like "mixed",
  "short", "lost", "damages", or blank -- these are internal stock
  adjustments and write-offs, not customer sales. Decision: EXCLUDED from
  fact_sales entirely during ETL, since they fall outside the fact
  table's defined grain (a real sales transaction).

- 4,382 rows (0.4%) have missing product descriptions. Handled via an
  "Unknown Product" placeholder in dim_product.

- Country distribution is heavily UK-dominant (92% of rows). Region
  grouping in dim_country reflects this explicitly rather than treating
  UK as one of many equally-weighted European countries.

## fact_sales

Grain: one row per invoice line item (real sales transactions only).

| Column | Type | Notes |
|---|---|---|
| sale_id | INTEGER (surrogate PK) | auto-incrementing |
| date_key | INTEGER (FK) | references dim_date |
| customer_key | INTEGER (FK) | references dim_customer; -1 for unknown |
| product_key | INTEGER (FK) | references dim_product |
| country_key | INTEGER (FK) | references dim_country |
| invoice_number | VARCHAR | natural key from source, kept for traceability |
| quantity | INTEGER | can be negative (returns) |
| unit_price | NUMERIC | |
| total_amount | NUMERIC | quantity * unit_price |
| is_return | BOOLEAN | derived from quantity < 0 |

## dim_date

| Column | Type | Notes |
|---|---|---|
| date_key | INTEGER (PK) | format YYYYMMDD |
| full_date | DATE | |
| year | INTEGER | |
| quarter | INTEGER | 1-4 |
| month | INTEGER | 1-12 |
| month_name | VARCHAR | |
| day_of_week | VARCHAR | |
| is_weekend | BOOLEAN | |

Generated programmatically for the full date range in the source data
(2009-12-01 to 2011-12-09), not derived row-by-row from the fact table.

## dim_customer

| Column | Type | Notes |
|---|---|---|
| customer_key | INTEGER (PK) | -1 reserved for "Unknown Customer" |
| customer_id | VARCHAR (natural key) | NULL for the Unknown Customer row |
| country | VARCHAR | customer's country from source data |
| first_purchase_date | DATE | derived: MIN(InvoiceDate) per customer |
| customer_segment | VARCHAR | NULL initially; populated in Module 4 (RFM/churn) |

## dim_product

| Column | Type | Notes |
|---|---|---|
| product_key | INTEGER (PK) | -1 reserved for "Unknown Product" |
| stock_code | VARCHAR (natural key) | |
| description | VARCHAR | "UNKNOWN" for the Unknown Product row |
| category | VARCHAR | derived via keyword-dictionary matching against description |

Category keyword dictionary (derived from description word-frequency
analysis on the actual data, priority-ordered so each product gets
exactly one category):

1. Christmas & Seasonal: CHRISTMAS, XMAS, EASTER, HALLOWEEN
2. Lighting: LIGHT, LAMP, CANDLE, T-LIGHT
3. Kitchen & Dining: CAKE, TEA, GLASS, BOTTLE, MUG, CUP, LUNCH
4. Bags & Storage: BAG, BOX, TIN, BASKET
5. Stationery & Paper: CARD, PAPER, NOTEBOOK, PENCIL
6. Home Decor: HEART, SIGN, HANGING, DECORATION, HOLDER
7. Other (fallback for unmatched products)

## dim_country

| Column | Type | Notes |
|---|---|---|
| country_key | INTEGER (PK) | |
| country_name | VARCHAR (natural key) | |
| region | VARCHAR | see grouping logic below |

Region grouping (reflecting the UK-dominant distribution found in EDA):
- "United Kingdom" -> its own region (92% of data; the home market)
- "EIRE", "Channel Islands" -> "UK & Ireland" (geographically/commercially closest)
- Continental European countries (Germany, France, Netherlands, Spain,
  etc.) -> "Europe"
- Australia and other non-European countries -> "Rest of World"
- "Unspecified" -> "Unknown"
