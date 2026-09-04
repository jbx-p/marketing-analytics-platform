"""
ETL pipeline: Online Retail II raw data -> PostgreSQL star schema warehouse.
Re-runnable and idempotent: each run drops and rebuilds all tables from
the raw source, so running it twice produces identical results.
"""

import os
import pandas as pd
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from dotenv import load_dotenv

CATEGORY_KEYWORDS = {
    "Christmas & Seasonal": ["CHRISTMAS", "XMAS", "EASTER", "HALLOWEEN"],
    "Lighting": ["LIGHT", "LAMP", "CANDLE", "T-LIGHT"],
    "Kitchen & Dining": ["CAKE", "TEA", "GLASS", "BOTTLE", "MUG", "CUP", "LUNCH"],
    "Bags & Storage": ["BAG", "BOX", "TIN", "BASKET"],
    "Stationery & Paper": ["CARD", "PAPER", "NOTEBOOK", "PENCIL"],
    "Home Decor": ["HEART", "SIGN", "HANGING", "DECORATION", "HOLDER"],
}

EUROPE_COUNTRIES = [
    "Germany", "France", "Netherlands", "Spain", "Switzerland", "Belgium",
    "Portugal", "Italy", "Norway", "Sweden", "Cyprus", "Finland", "Austria",
    "Denmark", "Greece", "Poland", "Malta", "Lithuania", "Lebanon"
]


def get_engine():
    load_dotenv()
    password_encoded = quote_plus(os.getenv("DB_PASSWORD"))
    db_url = f"postgresql://{os.getenv('DB_USER')}:{password_encoded}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    return create_engine(db_url)


def extract(path):
    print(f"[EXTRACT] Reading {path}")
    df = pd.read_csv(path)
    print(f"[EXTRACT] Raw rows: {len(df):,}")
    return df


def clean(df):
    df = df.rename(columns={"Customer ID": "customer_id_raw"})
    df.columns = [c.lower() for c in df.columns]

    before = len(df)
    df = df[df["price"] > 0].copy()
    print(f"[CLEAN] Excluded {before - len(df):,} zero/negative price rows (stock adjustments)")

    df["invoicedate"] = pd.to_datetime(df["invoicedate"])
    df["is_return"] = df["quantity"] < 0
    print(f"[CLEAN] Remaining rows: {len(df):,}")
    return df


def assign_region(country):
    if country == "United Kingdom":
        return "United Kingdom"
    elif country in ["EIRE", "Channel Islands"]:
        return "UK & Ireland"
    elif country == "Unspecified":
        return "Unknown"
    else:
        return "Europe" if country in EUROPE_COUNTRIES else "Rest of World"


def assign_category(description):
    if pd.isna(description):
        return "Other"
    desc_upper = str(description).upper()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in desc_upper for kw in keywords):
            return category
    return "Other"


def build_dim_date(df):
    date_range = pd.date_range(
        start=df["invoicedate"].min().normalize(),
        end=df["invoicedate"].max().normalize(),
        freq="D"
    )
    dim_date = pd.DataFrame({"full_date": date_range})
    dim_date["date_key"] = dim_date["full_date"].dt.strftime("%Y%m%d").astype(int)
    dim_date["year"] = dim_date["full_date"].dt.year
    dim_date["quarter"] = dim_date["full_date"].dt.quarter
    dim_date["month"] = dim_date["full_date"].dt.month
    dim_date["month_name"] = dim_date["full_date"].dt.month_name()
    dim_date["day_of_week"] = dim_date["full_date"].dt.day_name()
    dim_date["is_weekend"] = dim_date["full_date"].dt.dayofweek >= 5
    dim_date = dim_date[["date_key", "full_date", "year", "quarter", "month", "month_name", "day_of_week", "is_weekend"]]
    print(f"[TRANSFORM] dim_date: {len(dim_date)} rows")
    return dim_date


def build_dim_country(df):
    unique_countries = df["country"].dropna().unique()
    dim_country = pd.DataFrame({"country_name": unique_countries})
    dim_country["region"] = dim_country["country_name"].apply(assign_region)
    dim_country["country_key"] = range(1, len(dim_country) + 1)
    dim_country = dim_country[["country_key", "country_name", "region"]]
    print(f"[TRANSFORM] dim_country: {len(dim_country)} rows")
    return dim_country


def build_dim_product(df):
    product_desc = df.groupby("stockcode")["description"].agg(
        lambda x: x.mode()[0] if not x.mode().empty else "UNKNOWN"
    ).reset_index()
    product_desc.columns = ["stock_code", "description"]
    product_desc["description"] = product_desc["description"].fillna("UNKNOWN")
    product_desc["category"] = product_desc["description"].apply(assign_category)
    product_desc["product_key"] = range(1, len(product_desc) + 1)

    unknown_product = pd.DataFrame([{"product_key": -1, "stock_code": None, "description": "UNKNOWN", "category": "Other"}])
    dim_product = pd.concat([unknown_product, product_desc[["product_key", "stock_code", "description", "category"]]], ignore_index=True)
    print(f"[TRANSFORM] dim_product: {len(dim_product)} rows")
    return dim_product


def build_dim_customer(df):
    customer_info = df[df["customer_id_raw"].notna()].groupby("customer_id_raw").agg(
        country=("country", "first"),
        first_purchase_date=("invoicedate", "min")
    ).reset_index()
    customer_info.columns = ["customer_id", "country", "first_purchase_date"]
    customer_info["customer_key"] = range(1, len(customer_info) + 1)
    customer_info["customer_segment"] = None

    unknown_customer = pd.DataFrame([{
        "customer_key": -1, "customer_id": None, "country": None,
        "first_purchase_date": None, "customer_segment": None
    }])
    dim_customer = pd.concat([unknown_customer, customer_info[["customer_key", "customer_id", "country", "first_purchase_date", "customer_segment"]]], ignore_index=True)
    print(f"[TRANSFORM] dim_customer: {len(dim_customer)} rows")
    return dim_customer


def build_fact_sales(df, dim_country, dim_product, dim_customer):
    country_map = dict(zip(dim_country["country_name"], dim_country["country_key"]))
    product_map = dict(zip(dim_product["stock_code"], dim_product["product_key"]))
    customer_map = dict(zip(dim_customer["customer_id"], dim_customer["customer_key"]))

    fact_sales = df.copy()
    fact_sales["date_key"] = fact_sales["invoicedate"].dt.strftime("%Y%m%d").astype(int)
    fact_sales["country_key"] = fact_sales["country"].map(country_map)
    fact_sales["product_key"] = fact_sales["stockcode"].map(product_map).fillna(-1).astype(int)
    fact_sales["customer_key"] = fact_sales["customer_id_raw"].map(customer_map).fillna(-1).astype(int)
    fact_sales["total_amount"] = fact_sales["quantity"] * fact_sales["price"]

    fact_sales = fact_sales.rename(columns={"invoice": "invoice_number", "price": "unit_price"})
    fact_sales = fact_sales[[
        "date_key", "customer_key", "product_key", "country_key",
        "invoice_number", "quantity", "unit_price", "total_amount", "is_return"
    ]].reset_index(drop=True)
    fact_sales.insert(0, "sale_id", range(1, len(fact_sales) + 1))

    print(f"[TRANSFORM] fact_sales: {len(fact_sales):,} rows")
    return fact_sales


def quality_check(fact_sales):
    print("[QUALITY CHECK]")
    checks_passed = True
    for col in ["date_key", "customer_key", "product_key", "country_key"]:
        nulls = fact_sales[col].isna().sum()
        print(f"  Nulls in {col}: {nulls}")
        if nulls > 0:
            checks_passed = False

    revenue = fact_sales[~fact_sales["is_return"]]["total_amount"].sum()
    print(f"  Total revenue (excluding returns): ${revenue:,.2f}")

    if not checks_passed:
        raise ValueError("Data quality check FAILED: nulls found in foreign key columns. Fix before loading.")
    print("[QUALITY CHECK] Passed.")


def load(engine, dim_date, dim_country, dim_product, dim_customer, fact_sales):
    print("[LOAD] Writing tables to PostgreSQL (replacing existing)...")
    dim_date.to_sql("dim_date", engine, if_exists="replace", index=False)
    dim_country.to_sql("dim_country", engine, if_exists="replace", index=False)
    dim_product.to_sql("dim_product", engine, if_exists="replace", index=False)
    dim_customer.to_sql("dim_customer", engine, if_exists="replace", index=False)
    fact_sales.to_sql("fact_sales", engine, if_exists="replace", index=False, chunksize=10000, method="multi")
    print("[LOAD] Done.")


def main():
    engine = get_engine()
    df = extract("../data/raw/online_retail_II.csv")
    df = clean(df)

    dim_date = build_dim_date(df)
    dim_country = build_dim_country(df)
    dim_product = build_dim_product(df)
    dim_customer = build_dim_customer(df)
    fact_sales = build_fact_sales(df, dim_country, dim_product, dim_customer)

    quality_check(fact_sales)
    load(engine, dim_date, dim_country, dim_product, dim_customer, fact_sales)

    print("\n[ETL COMPLETE]")


if __name__ == "__main__":
    main()