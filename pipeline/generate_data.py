"""
generate_data.py
Zevo Marketing Analytics — Synthetic Data Generation

Generates 4 source tables (channels, campaigns, daily_spend, orders)
simulating 2 years of D2C skincare marketing performance across
Google Ads, Meta, Instagram, and Email.

Run: python generate_data.py
Output: zevo_data/*.csv
"""

# ============================================================
# CELL 1 — IMPORTS AND CONFIGURATION
# ============================================================

import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import date, timedelta

fake = Faker('en_IN')  # Indian locale
np.random.seed(42)
random.seed(42)

print("✓ All libraries loaded. Zevo data generation ready.")

# ============================================================
# CELL 2 — GENERATE CHANNELS TABLE
# 4 rows — one per marketing channel
# ============================================================

channels_data = [
    {'channel_id': 'CH001', 'channel_name': 'Google Ads',  'channel_type': 'Paid'},
    {'channel_id': 'CH002', 'channel_name': 'Meta',        'channel_type': 'Paid'},
    {'channel_id': 'CH003', 'channel_name': 'Instagram',   'channel_type': 'Paid'},
    {'channel_id': 'CH004', 'channel_name': 'Email',       'channel_type': 'Owned'},
]

df_channels = pd.DataFrame(channels_data)
print(f"✓ Channels table created: {len(df_channels)} rows")
print(df_channels)

# ============================================================
# CELL 3 — GENERATE CAMPAIGNS TABLE
# 136 campaigns across 4 channels and 2 years
# Instagram over-invested, Google under-invested
# Email ignored despite best returns
# All campaign end dates capped to Dec 31 2024
# ============================================================

campaign_templates = {
    'CH001': ['Search - Brand Keywords', 'Search - Competitor Keywords',
              'Search - Skincare Generic', 'Performance Max - Acquisition',
              'Search - Moisturizer', 'Search - Sunscreen', 'Search - Serum',
              'Performance Max - Retargeting', 'Search - Anti Aging',
              'Search - Face Wash', 'Search - Night Cream', 'Search - Toner',
              'Performance Max - New Users', 'Search - SPF Cream',
              'Search - Vitamin C Serum', 'Search - Hydrating Cream',
              'Performance Max - Seasonal', 'Search - Eye Cream',
              'Search - Exfoliator', 'Search - Brightening Serum'],

    'CH002': ['Feed - Awareness', 'Feed - Conversion', 'Feed - Retargeting',
              'Video - Brand Story', 'Feed - Product Launch',
              'Feed - Festival Offer', 'Feed - Lookalike Audience',
              'Video - Testimonial', 'Feed - Seasonal Push',
              'Feed - New Collection', 'Video - Skincare Routine',
              'Feed - Flash Sale', 'Feed - Before After',
              'Video - Founder Story', 'Feed - Bundle Offer',
              'Feed - Winter Campaign', 'Feed - Summer Campaign',
              'Video - Ingredient Spotlight', 'Feed - Referral Push',
              'Feed - Loyalty Campaign', 'Feed - Re Engagement',
              'Feed - Category Expansion'],

    'CH003': ['Reels - Brand Awareness', 'Stories - Flash Sale',
              'Reels - Influencer Collab', 'Stories - Product Highlight',
              'Reels - Festival Campaign', 'Stories - Discount Push',
              'Reels - Skincare Routine', 'Stories - New Launch',
              'Reels - Before After', 'Stories - Bundle Offer',
              'Reels - Ingredient Story', 'Stories - User Testimonial',
              'Reels - Morning Routine', 'Stories - Limited Offer',
              'Reels - Founder Story', 'Stories - Seasonal Push',
              'Reels - Tutorial', 'Stories - Re Engagement',
              'Reels - Giveaway', 'Stories - Poll Campaign',
              'Reels - Community Post', 'Stories - Winter Skin'],

    'CH004': ['Welcome Series', 'Abandoned Cart Recovery',
              'Monthly Newsletter', 'Festival Offer Blast',
              'Win Back Campaign', 'Loyalty Reward Email',
              'New Launch Announcement', 'Seasonal Sale Email',
              'Post Purchase Follow Up', 'Re Engagement Series',
              'Birthday Offer Email', 'VIP Customer Reward',
              'Product Education Series', 'Flash Sale Alert',
              'Referral Program Email', 'Summer Skincare Tips',
              'Winter Care Guide', 'Bundle Offer Email',
              'Survey Email', 'Subscription Reminder'],
}

# Budget ranges per channel per year (INR)
budget_ranges = {
    'CH001': {'2023': (40000, 120000), '2024': (80000, 200000)},
    'CH002': {'2023': (30000, 90000),  '2024': (60000, 140000)},
    'CH003': {'2023': (25000, 70000),  '2024': (30000, 85000)},  # Scales up — mistake
    'CH004': {'2023': (5000,  12000),  '2024': (8000,  18000)},  # Stays low — ignored
}

# Campaign counts — Instagram over-invested, Email ignored
campaign_counts = {
    'CH001': {'2023': 14, '2024': 18},  # Google — underinvested but consistent
    'CH002': {'2023': 18, '2024': 22},  # Meta — middling, keeps growing
    'CH003': {'2023': 20, '2024': 22},  # Instagram — scales into inefficiency
    'CH004': {'2023': 10, '2024': 12},  # Email — ignored despite best returns
}

# Campaign duration ranges in days per channel
duration_ranges = {
    'CH001': (30, 60),
    'CH002': (14, 35),
    'CH003': (7,  21),
    'CH004': (3,  10),
}

# Hard cap — no data beyond this date
dataset_end = date(2024, 12, 31)

campaigns = []
campaign_id = 1

for channel in channels_data:
    cid = channel['channel_id']
    cname = channel['channel_name']
    templates = campaign_templates[cid]

    for year in ['2023', '2024']:
        count = campaign_counts[cid][year]
        used_names = []

        for i in range(count):
            # Pick unique campaign name
            available = [t for t in templates if t not in used_names]
            if not available:
                available = templates
            name = random.choice(available)
            used_names.append(name)

            # Random start date within the year
            # Leave room at end of year for campaign to run
            year_start = date(int(year), 1, 1)
            year_end   = date(int(year), 11, 30)
            days_in_year = (year_end - year_start).days
            start_offset = random.randint(0, days_in_year)
            start_date = year_start + timedelta(days=start_offset)

            # Duration
            min_dur, max_dur = duration_ranges[cid]
            duration = random.randint(min_dur, max_dur)
            end_date = start_date + timedelta(days=duration)

            # Hard cap end date to Dec 31 2024
            end_date = min(end_date, dataset_end)

            # Budget
            min_budget, max_budget = budget_ranges[cid][year]
            budget = round(random.uniform(min_budget, max_budget), 2)

            campaigns.append({
                'campaign_id':   f'CAM{campaign_id:03d}',
                'campaign_name': f'{cname} — {name} {year}',
                'channel_id':    cid,
                'year':          int(year),
                'start_date':    start_date,
                'end_date':      end_date,
                'total_budget':  budget,
            })
            campaign_id += 1

df_campaigns = pd.DataFrame(campaigns)

# Verify no dates beyond 2024
assert df_campaigns['end_date'].max() <= dataset_end, "Date cap failed!"

print(f"✓ Campaigns table created: {len(df_campaigns)} campaigns")
print(f"✓ Latest end date: {df_campaigns['end_date'].max()} — within bounds")
print(f"\nCampaign count per channel per year:")
print(df_campaigns.groupby(['channel_id', 'year'])['campaign_id'].count())
print(f"\nBudget summary per channel:")
print(df_campaigns.groupby('channel_id')['total_budget'].agg(['sum', 'mean']).round(2))

# ============================================================
# CELL 4 — GENERATE DAILY SPEND TABLE WITH AD SETS
# Each campaign splits into coherent ad sets
# Ad set behavior influences CTR and conversion realistically
# Instagram deteriorates in 2024, Google plateaus
# Email has no ad sets — one row per day per campaign
# Email clicks capped realistically — small but growing list
# ============================================================

# Ad sets per channel with performance personality
ad_set_templates = {
    'CH001': [
        {'name': 'Brand Keywords',            'ctr_mult': 1.4, 'spend_share': 0.25},
        {'name': 'Product Intent Keywords',   'ctr_mult': 1.2, 'spend_share': 0.35},
        {'name': 'Generic Skincare Keywords', 'ctr_mult': 0.8, 'spend_share': 0.40},
    ],
    'CH002': [
        {'name': 'Warm Audiences',            'ctr_mult': 1.3, 'spend_share': 0.20},
        {'name': 'Site Visitors',             'ctr_mult': 1.1, 'spend_share': 0.25},
        {'name': 'Cart Abandoners',           'ctr_mult': 1.5, 'spend_share': 0.15},
        {'name': 'Broad Targeting',           'ctr_mult': 0.7, 'spend_share': 0.40},
    ],
    'CH003': [
        {'name': 'Prospecting',               'ctr_mult': 0.6, 'spend_share': 0.40},
        {'name': 'Retargeting',               'ctr_mult': 1.2, 'spend_share': 0.25},
        {'name': 'Influencer Lookalike',      'ctr_mult': 0.9, 'spend_share': 0.20},
        {'name': 'Interest Based Skincare',   'ctr_mult': 0.8, 'spend_share': 0.15},
    ],
    'CH004': None,  # No ad sets for Email
}

# CTR base ranges per channel per year
ctr_ranges = {
    'CH001': {'2023': (0.040, 0.060), '2024': (0.035, 0.055)},  # Slight plateau
    'CH002': {'2023': (0.015, 0.025), '2024': (0.018, 0.028)},  # Slight improvement
    'CH003': {'2023': (0.012, 0.018), '2024': (0.006, 0.010)},  # Deteriorates
    'CH004': {'2023': (0.180, 0.250), '2024': (0.200, 0.270)},  # Improves
}

# CPC ranges per channel per year (INR)
cpc_ranges = {
    'CH001': {'2023': (18, 32), '2024': (24, 40)},  # Rises — competition
    'CH002': {'2023': (10, 20), '2024': (12, 22)},  # Slight rise
    'CH003': {'2023': (8,  16), '2024': (10, 20)},  # Rises + CTR drops — bad combo
    'CH004': {'2023': (1,  3),  '2024': (1,  3)},   # Flat — email cost
}

# Festival periods
festival_dates = [
    (date(2023, 10, 20), date(2023, 10, 26)),  # Diwali 2023
    (date(2023, 2,  10), date(2023, 2,  15)),  # Valentine's 2023
    (date(2023, 11, 24), date(2023, 11, 27)),  # Black Friday 2023
    (date(2024, 11, 1),  date(2024, 11, 7)),   # Diwali 2024
    (date(2024, 2,  10), date(2024, 2,  15)),  # Valentine's 2024
    (date(2024, 11, 29), date(2024, 12, 2)),   # Black Friday 2024
]

def is_festival(d):
    for start, end in festival_dates:
        if start <= d <= end:
            return True
    return False

def is_weekend(d):
    return d.weekday() >= 5

def spend_multiplier(d):
    multiplier = 1.0
    if is_festival(d):
        multiplier *= random.uniform(1.3, 1.6)
    if is_weekend(d):
        multiplier *= random.uniform(1.1, 1.25)
    return multiplier

def ramp_factor(day_index, total_days):
    progress = day_index / total_days
    if progress < 0.15:
        return random.uniform(0.4, 0.6)
    elif progress < 0.75:
        return random.uniform(0.85, 1.15)
    else:
        return random.uniform(0.6, 0.85)

daily_spend_records = []
spend_id = 1

for _, camp in df_campaigns.iterrows():
    cid = camp['channel_id']
    year = str(camp['year'])
    total_budget = camp['total_budget']
    start = pd.to_datetime(camp['start_date']).date()
    end = pd.to_datetime(camp['end_date']).date()
    total_days = (end - start).days + 1
    base_daily = total_budget / total_days
    ad_sets = ad_set_templates[cid]

    current_date = start
    day_index = 0

    while current_date <= end:
        ramp = ramp_factor(day_index, total_days)
        festival = spend_multiplier(current_date)
        total_daily = base_daily * ramp * festival

        if ad_sets is None:
            # Email — single row per day
            # Small but engaged and growing list
            # Clicks based on list size, not spend
            daily = round(total_daily * random.uniform(0.85, 1.15), 2)
            ctr = random.uniform(*ctr_ranges[cid][year])

            if year == '2023':
                clicks = random.randint(80, 200)
            else:
                clicks = random.randint(150, 350)

            impressions = int(clicks / ctr) if ctr > 0 else 0

            daily_spend_records.append({
                'spend_id':     f'SPD{spend_id:06d}',
                'campaign_id':  camp['campaign_id'],
                'channel_id':   cid,
                'ad_set_name':  'Email Send',
                'date':         current_date,
                'amount_spent': daily,
                'impressions':  impressions,
                'clicks':       clicks,
            })
            spend_id += 1

        else:
            # Paid channels — one row per ad set per day
            for ad_set in ad_sets:
                ad_daily = round(
                    total_daily * ad_set['spend_share'] * random.uniform(0.85, 1.15), 2
                )
                base_ctr = random.uniform(*ctr_ranges[cid][year])
                ctr = round(base_ctr * ad_set['ctr_mult'], 4)
                cpc = random.uniform(*cpc_ranges[cid][year])
                clicks = int(ad_daily / cpc)
                impressions = int(clicks / ctr) if ctr > 0 else 0

                daily_spend_records.append({
                    'spend_id':     f'SPD{spend_id:06d}',
                    'campaign_id':  camp['campaign_id'],
                    'channel_id':   cid,
                    'ad_set_name':  ad_set['name'],
                    'date':         current_date,
                    'amount_spent': ad_daily,
                    'impressions':  impressions,
                    'clicks':       clicks,
                })
                spend_id += 1

        current_date += timedelta(days=1)
        day_index += 1

df_daily_spend = pd.DataFrame(daily_spend_records)
print(f"✓ Daily spend table created: {len(df_daily_spend)} rows")
print(f"\nTotal spend per channel (INR):")
print(df_daily_spend.groupby('channel_id')['amount_spent'].sum().round(2))
print(f"\nTotal clicks per channel:")
print(df_daily_spend.groupby('channel_id')['clicks'].sum())

# ============================================================
# CELL 5 — GENERATE ORDERS TABLE
# Every order links to a campaign
# Revenue reflects channel conversion personality
# Instagram: acceptable 2023, deteriorates 2024
# Google: consistent, moderate scalability, CPC rising
# Meta: middling, slight improvement 2024
# Email: best ROAS but believable — rebalanced to 8-12x
# Discount frequency varies by channel
# ============================================================

# Conversion rates per channel per year
# (orders generated per click)
conversion_rates = {
    'CH001': {'2023': (0.030, 0.050), '2024': (0.028, 0.045)},  # Slight plateau
    'CH002': {'2023': (0.015, 0.025), '2024': (0.018, 0.028)},  # Slight improvement
    'CH003': {'2023': (0.012, 0.018), '2024': (0.006, 0.010)},  # Deteriorates
    'CH004': {'2023': (0.020, 0.035), '2024': (0.025, 0.040)},  # Strong but believable
}

# Average order value ranges per channel (INR)
aov_ranges = {
    'CH001': {'2023': (1800, 2500), '2024': (1800, 2500)},  # Stable
    'CH002': {'2023': (1200, 1800), '2024': (1300, 1900)},  # Slight improvement
    'CH003': {'2023': (900,  1500), '2024': (800,  1300)},  # Drops — more discounting
    'CH004': {'2023': (1600, 2200), '2024': (1700, 2300)},  # Good AOV, loyal customers
}

# Discount frequency per channel
# Probability that an order has a discount applied
discount_probability = {
    'CH001': 0.15,  # Low — intent buyers
    'CH002': 0.25,  # Moderate
    'CH003': 0.45,  # High — compensating for poor conversion
    'CH004': 0.10,  # Low — loyal customers
}

# Discount impact on AOV
discount_aov_reduction = 0.15  # 15% lower AOV when discount applied

# Product categories Zevo sells
product_categories = [
    'Moisturizer',
    'Sunscreen',
    'Serum',
    'Face Wash',
    'Toner',
    'Eye Cream',
    'Night Cream',
    'Exfoliator',
]

# Category weights per channel
category_weights = {
    'CH001': [0.20, 0.20, 0.20, 0.15, 0.10, 0.05, 0.05, 0.05],
    'CH002': [0.25, 0.15, 0.20, 0.15, 0.10, 0.05, 0.05, 0.05],
    'CH003': [0.30, 0.10, 0.25, 0.15, 0.10, 0.04, 0.04, 0.02],
    'CH004': [0.15, 0.15, 0.20, 0.15, 0.10, 0.10, 0.10, 0.05],
}

orders = []
order_id = 1

# Get total clicks per campaign from daily spend
campaign_clicks = (
    df_daily_spend.groupby(['campaign_id', 'channel_id'])['clicks']
    .sum()
    .reset_index()
)

for _, row in campaign_clicks.iterrows():
    cid = row['channel_id']
    camp_id = row['campaign_id']
    total_clicks = row['clicks']

    # Get year and dates from campaigns table
    camp_row = df_campaigns[df_campaigns['campaign_id'] == camp_id].iloc[0]
    year = str(camp_row['year'])
    start = pd.to_datetime(camp_row['start_date']).date()
    end = pd.to_datetime(camp_row['end_date']).date()

    # Total orders from this campaign
    conv_rate = random.uniform(*conversion_rates[cid][year])
    total_orders = int(total_clicks * conv_rate)

    if total_orders == 0:
        continue

    # Spread orders randomly across campaign duration
    campaign_days = (end - start).days + 1

    for _ in range(total_orders):
        order_date = start + timedelta(days=random.randint(0, campaign_days - 1))

        # Discount logic
        has_discount = random.random() < discount_probability[cid]

        # AOV
        min_aov, max_aov = aov_ranges[cid][year]
        revenue = round(random.uniform(min_aov, max_aov), 2)
        if has_discount:
            revenue = round(revenue * (1 - discount_aov_reduction), 2)

        # Product category
        category = random.choices(
            product_categories,
            weights=category_weights[cid]
        )[0]

        orders.append({
            'order_id':         f'ORD{order_id:06d}',
            'campaign_id':      camp_id,
            'channel_id':       cid,
            'order_date':       order_date,
            'revenue':          revenue,
            'product_category': category,
            'discount_applied': has_discount,
            'year':             int(year),
        })
        order_id += 1

df_orders = pd.DataFrame(orders)
df_orders = df_orders.sort_values('order_date').reset_index(drop=True)

print(f"✓ Orders table created: {len(df_orders)} rows")
print(f"\nOrders and revenue per channel:")
print(df_orders.groupby('channel_id').agg(
    total_orders=('order_id', 'count'),
    total_revenue=('revenue', 'sum'),
).round(2))

# ============================================================
# CELL 6 — EXPORT ALL TABLES TO CSV
# Save all 4 tables as clean CSV files
# Ready for review before PostgreSQL ingestion
# ============================================================

import os

# Create output folder if it doesn't exist
output_folder = 'zevo_data'
os.makedirs(output_folder, exist_ok=True)

# Export all 4 tables
df_channels.to_csv(f'{output_folder}/channels.csv', index=False)
df_campaigns.to_csv(f'{output_folder}/campaigns.csv', index=False)
df_daily_spend.to_csv(f'{output_folder}/daily_spend.csv', index=False)
df_orders.to_csv(f'{output_folder}/orders.csv', index=False)

print("✓ All tables exported to CSV successfully")
print(f"\nFiles saved in: {output_folder}/")
print(f"  channels.csv     — {len(df_channels)} rows")
print(f"  campaigns.csv    — {len(df_campaigns)} rows")
print(f"  daily_spend.csv  — {len(df_daily_spend)} rows")
print(f"  orders.csv       — {len(df_orders)} rows")
print(f"\nTotal rows exported: {len(df_channels) + len(df_campaigns) + len(df_daily_spend) + len(df_orders):,}")