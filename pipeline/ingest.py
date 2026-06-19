"""
ingest.py
Zevo Marketing Analytics — Feature Engineering + PostgreSQL Ingestion

Reads the 4 CSVs produced by generate_data.py, adds engineered columns
(CTR, festival flags, revenue buckets, time fields), and loads
everything into the PostgreSQL 'raw' schema.

Requires a running PostgreSQL instance with a database created
(see README for setup). Set credentials via environment variables
or edit the defaults below for local use.

Run: python ingest.py
"""

# ============================================================
# CELL 1 — DATABASE CONNECTION
# Establishing connection to PostgreSQL zevo_analytics database
# SQLAlchemy creates a connection engine —
# think of it as a bridge between Python and PostgreSQL
# ============================================================

import os
from sqlalchemy import create_engine, text
import pandas as pd
import numpy as np

# PostgreSQL credentials — set these as environment variables,
# or replace the defaults below for local runs.
# Example (Windows cmd):  set DB_PASSWORD=yourpassword
# Example (Mac/Linux):    export DB_PASSWORD=yourpassword
DB_USER     = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'your_password_here')
DB_HOST     = os.environ.get('DB_HOST', 'localhost')
DB_PORT     = os.environ.get('DB_PORT', '5432')
DB_NAME     = os.environ.get('DB_NAME', 'Zevo_analytics')

# Create the engine — this is the connection bridge
engine = create_engine(
    f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
)

# Test the connection
with engine.connect() as conn:
    conn.execute(text('SELECT 1'))

print(f"✓ Connected to PostgreSQL — {DB_NAME} database")

# ============================================================
# CELL 2 — LOAD CSV FILES
# Reading all 4 cleaned CSV files into Python
# Expects generate_data.py to have been run first,
# producing CSVs in the zevo_data/ folder.
# ============================================================

# Load all 4 tables — relative path, works from project root
channels    = pd.read_csv('zevo_data/channels.csv')
campaigns   = pd.read_csv('zevo_data/campaigns.csv')
daily_spend = pd.read_csv('zevo_data/daily_spend.csv')
orders      = pd.read_csv('zevo_data/orders.csv')

# Convert date columns to proper datetime format
campaigns['start_date']   = pd.to_datetime(campaigns['start_date'])
campaigns['end_date']     = pd.to_datetime(campaigns['end_date'])
daily_spend['date']       = pd.to_datetime(daily_spend['date'])
orders['order_date']      = pd.to_datetime(orders['order_date'])

# Quick confirmation
print("✓ All CSVs loaded successfully")
print(f"  channels:    {len(channels)} rows")
print(f"  campaigns:   {len(campaigns)} rows")
print(f"  daily_spend: {len(daily_spend)} rows")
print(f"  orders:      {len(orders)} rows")

# ============================================================
# CELL 3 — FEATURE ENGINEERING — CAMPAIGNS
# Adding 3 new columns to campaigns table:
# 1. duration_days  — how long the campaign ran
# 2. start_month    — which month it started
# 3. start_quarter  — which quarter it started
# ============================================================

# 1. Duration in days — end date minus start date
campaigns['duration_days'] = (
    campaigns['end_date'] - campaigns['start_date']
).dt.days

# 2. Start month — extract month number from start date
campaigns['start_month'] = campaigns['start_date'].dt.month

# 3. Start quarter — extract quarter from start date
campaigns['start_quarter'] = campaigns['start_date'].dt.quarter

# Verify
print("✓ Campaigns feature engineering done")
print(f"\nNew columns added:")
print(campaigns[['campaign_id', 'start_date', 'end_date', 
                  'duration_days', 'start_month', 
                  'start_quarter']].head(5))
print(f"\nDuration stats:")
print(campaigns['duration_days'].describe().round(1))

# ============================================================
# CELL 4 — FEATURE ENGINEERING — DAILY SPEND
# Adding 6 new columns to daily_spend table:
# 1. ctr          — click through rate (clicks / impressions)
# 2. month        — month number from date
# 3. quarter      — quarter from date
# 4. day_of_week  — Monday, Tuesday etc.
# 5. is_weekend   — True if Saturday or Sunday
# 6. is_festival  — True if date falls in a festival period
# ============================================================

# 1. CTR — clicks divided by impressions
# Replace 0 impressions with NaN to avoid division by zero
daily_spend['ctr'] = (
    daily_spend['clicks'] / daily_spend['impressions'].replace(0, np.nan)
).round(4)

# 2. Month
daily_spend['month'] = daily_spend['date'].dt.month

# 3. Quarter
daily_spend['quarter'] = daily_spend['date'].dt.quarter

# 4. Day of week
daily_spend['day_of_week'] = daily_spend['date'].dt.day_name()

# 5. Is weekend — Saturday = 5, Sunday = 6
daily_spend['is_weekend'] = daily_spend['date'].dt.dayofweek >= 5

# 6. Festival flag — dates within known festival periods
festival_periods = [
    ('2023-10-20', '2023-10-26'),  # Diwali 2023
    ('2023-02-10', '2023-02-15'),  # Valentine's 2023
    ('2023-11-24', '2023-11-27'),  # Black Friday 2023
    ('2024-11-01', '2024-11-07'),  # Diwali 2024
    ('2024-02-10', '2024-02-15'),  # Valentine's 2024
    ('2024-11-29', '2024-12-02'),  # Black Friday 2024
]

def is_festival(d):
    for start, end in festival_periods:
        if pd.Timestamp(start) <= d <= pd.Timestamp(end):
            return True
    return False

daily_spend['is_festival'] = daily_spend['date'].apply(is_festival)

# Verify
print("✓ Daily spend feature engineering done")
print(f"\nNew columns added:")
print(daily_spend[['spend_id', 'date', 'clicks', 'impressions',
                    'ctr', 'month', 'quarter',
                    'day_of_week', 'is_weekend',
                    'is_festival']].head(5))
print(f"\nCTR stats by channel:")
print(daily_spend.groupby('channel_id')['ctr'].mean().round(4))
print(f"\nFestival rows: {daily_spend['is_festival'].sum()}")
print(f"Weekend rows:  {daily_spend['is_weekend'].sum()}")

# ============================================================
# CELL 5 — FEATURE ENGINEERING — ORDERS
# Adding 4 new columns to orders table:
# 1. month          — month number from order date
# 2. quarter        — quarter from order date
# 3. is_festival    — True if order placed during festival
# 4. revenue_bucket — Low / Mid / High based on distribution
# ============================================================

# 1. Month
orders['month'] = orders['order_date'].dt.month

# 2. Quarter
orders['quarter'] = orders['order_date'].dt.quarter

# 3. Festival flag — reusing same festival periods
orders['is_festival'] = orders['order_date'].apply(is_festival)

# 4. Revenue bucket — based on actual data distribution
# First let's see the distribution
print("Revenue distribution:")
print(orders['revenue'].describe().round(2))

p33 = orders['revenue'].quantile(0.33)
p67 = orders['revenue'].quantile(0.67)

print(f"\n33rd percentile: ₹{p33:.2f}")
print(f"67th percentile: ₹{p67:.2f}")

# Create buckets based on distribution
def revenue_bucket(r):
    if r < p33:
        return 'Low'
    elif r < p67:
        return 'Mid'
    else:
        return 'High'

orders['revenue_bucket'] = orders['revenue'].apply(revenue_bucket)

# Verify
print(f"\n✓ Orders feature engineering done")
print(f"\nRevenue bucket distribution:")
print(orders['revenue_bucket'].value_counts())
print(f"\nSample rows:")
print(orders[['order_id', 'order_date', 'revenue',
              'month', 'quarter',
              'is_festival', 'revenue_bucket']].head(5))
print(f"\nFestival orders: {orders['is_festival'].sum()}")

# ============================================================
# CELL 6 — AUTO INGESTION INTO POSTGRESQL RAW SCHEMA
# Loads all 4 feature engineered tables into PostgreSQL
# schema = 'raw' — this is where raw data lives
# if_exists = 'replace' — overwrites if table already exists
# ============================================================

print("Ingesting tables into PostgreSQL raw schema...")
print("=" * 50)

# 1. Channels
channels.to_sql(
    'channels',
    engine,
    schema='raw',
    if_exists='replace',
    index=False
)
print(f"✓ raw.channels     — {len(channels)} rows")

# 2. Campaigns
campaigns.to_sql(
    'campaigns',
    engine,
    schema='raw',
    if_exists='replace',
    index=False
)
print(f"✓ raw.campaigns    — {len(campaigns)} rows")

# 3. Daily Spend
daily_spend.to_sql(
    'daily_spend',
    engine,
    schema='raw',
    if_exists='replace',
    index=False
)
print(f"✓ raw.daily_spend  — {len(daily_spend)} rows")

# 4. Orders
orders.to_sql(
    'orders',
    engine,
    schema='raw',
    if_exists='replace',
    index=False
)
print(f"✓ raw.orders       — {len(orders)} rows")

print("=" * 50)
print("✓ All tables ingested into PostgreSQL raw schema")

# ============================================================
# CELL 7 — VERIFICATION
# Query PostgreSQL directly to confirm
# row counts and column names match what we ingested
# ============================================================

from sqlalchemy import text

print("Verifying tables in PostgreSQL raw schema...")
print("=" * 50)

with engine.connect() as conn:

    # Check row counts
    for table in ['channels', 'campaigns', 'daily_spend', 'orders']:
        result = conn.execute(text(f"SELECT COUNT(*) FROM raw.{table}"))
        count = result.fetchone()[0]
        print(f"✓ raw.{table}: {count} rows")

    print("\nColumn check — raw.campaigns:")
    result = conn.execute(text("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'raw'
        AND table_name = 'campaigns'
        ORDER BY ordinal_position
    """))
    for row in result:
        print(f"  {row[0]:<20} {row[1]}")

    print("\nColumn check — raw.orders:")
    result = conn.execute(text("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'raw'
        AND table_name = 'orders'
        ORDER BY ordinal_position
    """))
    for row in result:
        print(f"  {row[0]:<20} {row[1]}")

print("=" * 50)
print("✓ Verification complete. Phase 2 done.")