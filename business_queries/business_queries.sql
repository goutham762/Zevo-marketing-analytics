-- ============================================================
-- Query 1: Channel ROAS Comparison
-- Which channel gives Zevo the best return on every rupee spent?
-- Finding: Email ROAS 7.98 — best performer, chronically underfunded
-- Finding: Instagram ROAS 0.90 — loss making, overfunded
-- ============================================================

select
    channel_name,
    total_spend,
    total_revenue,
    roas
from mart.mart_channel_roas
order by roas desc;

-- ============================================================
-- Query 2: Budget vs Actual Spend
-- Did Zevo spend what they planned per channel?
-- Finding: All channels 88-92% budget utilization
-- Problem wasn't overspending — it was spending in wrong channels
-- ============================================================

select
    channel_name,
    total_budget,
    total_spend,
    budget_utilization_pct
from mart.mart_channel_roas
order by budget_utilization_pct desc;

-- ============================================================
-- Query 3: Instagram Year Over Year Deterioration
-- How badly did Instagram decline from 2023 to 2024?
-- Finding: Spend +34%, Revenue -49%, ROAS 1.40 → 0.53
-- Finding: CTR halved, orders dropped 42%, cost per order +131%
-- Conclusion: Audience fatigue as spend scaled
-- ============================================================

select
    year,
    year_label,
    total_spend,
    total_revenue,
    avg_ctr,
    total_orders,
    roas,
    cost_per_order
from mart.mart_instagram_deterioration
order by year asc;

-- ============================================================
-- Query 4a: Top 10 Campaigns by ROAS
-- Best performing campaigns across 2 years
-- Finding: Top 10 are all Email campaigns
-- ============================================================

select
    campaign_name,
    channel_name,
    year,
    total_spend,
    total_revenue,
    roas,
    performance_verdict
from mart.mart_campaign_performance
order by roas desc
limit 10;

-- ============================================================
-- Query 4b: Bottom 10 Campaigns by ROAS
-- Worst performing campaigns — biggest budget wasters
-- Finding: Bottom 10 are all Instagram 2024 campaigns
-- Conclusion: Audience fatigue destroyed campaign performance
-- ============================================================

select
    campaign_name,
    channel_name,
    year,
    total_spend,
    total_revenue,
    roas,
    performance_verdict
from mart.mart_campaign_performance
order by roas asc
limit 10;

-- ============================================================
-- Query 5: Monthly Revenue vs Spend Trend
-- How did overall efficiency move month by month?
-- Finding: 2024 spend scaled significantly
-- Finding: ROAS declining in Q3/Q4 2024 — Instagram effect
-- ============================================================

select
    year,
    month,
    round(sum(monthly_spend)::numeric, 2)       as total_spend,
    round(sum(monthly_revenue)::numeric, 2)     as total_revenue,
    round(
        sum(monthly_revenue)::numeric /
        nullif(sum(monthly_spend)::numeric, 0)
    , 2)                                        as overall_roas
from mart.mart_monthly_trends
group by year, month
order by year asc, month asc;

-- ============================================================
-- Query 6: 90-Day Budget Reallocation Test Projection
-- Reduce Instagram spend by 30% over 90 days
-- Reallocate freed budget: Google 60%, Email 40%
-- Logic: Google feeds acquisition funnel, Email monetizes base
-- Assumes stable ROAS for Google and Email at higher spend
-- ============================================================

with instagram_monthly as (

    -- Step 1: Find Instagram 90 day spend
    select
        round(total_spend / 24 * 3, 2)     as instagram_90day_spend,
        roas                                as instagram_roas
    from mart.mart_channel_roas
    where channel_name = 'Instagram'

),

freed_budget as (

    -- Step 2: Calculate 30% reduction = freed budget
    -- Split: Google 60%, Email 40%
    select
        instagram_90day_spend,
        instagram_roas,
        round(instagram_90day_spend * 0.30, 2)          as freed_budget,
        round(instagram_90day_spend * 0.30 * 0.60, 2)   as google_additional_spend,
        round(instagram_90day_spend * 0.30 * 0.40, 2)   as email_additional_spend
    from instagram_monthly

),

channel_roas as (

    -- Step 3: Pull proven ROAS for Google and Email
    select
        max(case when channel_name = 'Google Ads'
            then roas end)                  as google_roas,
        max(case when channel_name = 'Email'
            then roas end)                  as email_roas
    from mart.mart_channel_roas

),

projected as (

    -- Step 4: Project revenue from reallocation
    select
        f.instagram_90day_spend,
        f.freed_budget,
        f.google_additional_spend,
        f.email_additional_spend,

        -- Revenue generated by reallocated budget
        round((f.google_additional_spend * r.google_roas)::numeric, 2)
                                            as google_projected_revenue,
        round((f.email_additional_spend * r.email_roas)::numeric, 2)
                                            as email_projected_revenue,

        -- Revenue lost from reducing Instagram
        round((f.freed_budget * f.instagram_roas)::numeric, 2)
                                            as instagram_lost_revenue,

        -- Cost of inaction — what Instagram burns in 90 days
        round((f.instagram_90day_spend * f.instagram_roas)::numeric, 2)
                                            as instagram_90day_revenue,
        round((f.instagram_90day_spend -
              (f.instagram_90day_spend * f.instagram_roas))::numeric, 2)
                                            as cost_of_inaction

    from freed_budget f
    cross join channel_roas r

)

-- Step 5: Final summary
select
    instagram_90day_spend                   as instagram_90day_spend,
    freed_budget                            as budget_freed_by_30pct_cut,
    google_additional_spend                 as google_extra_spend,
    email_additional_spend                  as email_extra_spend,
    google_projected_revenue                as google_extra_revenue,
    email_projected_revenue                 as email_extra_revenue,
    instagram_lost_revenue                  as instagram_lost_revenue,
    round((google_projected_revenue +
           email_projected_revenue -
           instagram_lost_revenue)::numeric, 2)
                                            as net_revenue_gain_90days,
    cost_of_inaction                        as money_lost_if_nothing_changes
from projected