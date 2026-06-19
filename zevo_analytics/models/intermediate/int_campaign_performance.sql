{{ config(schema='staging') }}

-- ============================================================
-- int_campaign_performance.sql
-- Joins campaigns + daily_spend + orders
-- One row per campaign showing full spend vs revenue picture
-- Foundation model — everything else builds on this
-- CTR already calculated in staging — reused here
-- ROAS, conversion rate, cost per order calculated here
-- ============================================================

with campaigns as (

    select * from {{ ref('stg_campaigns') }}

),

spend as (

    select
        campaign_id,
        sum(amount_spent)       as total_spend,
        sum(impressions)        as total_impressions,
        sum(clicks)             as total_clicks,
        avg(ctr)                as avg_ctr
    from {{ ref('stg_daily_spend') }}
    group by campaign_id

),

orders as (

    select
        campaign_id,
        count(order_id)         as total_orders,
        sum(revenue)            as total_revenue,
        avg(revenue)            as avg_order_value
    from {{ ref('stg_orders') }}
    group by campaign_id

)

select
    c.campaign_id,
    c.campaign_name,
    c.channel_id,
    c.year,
    c.start_date,
    c.end_date,
    c.duration_days,
    c.start_quarter,
    c.total_budget,

    -- Spend metrics
    round(cast(coalesce(s.total_spend, 0) as numeric), 2)        as total_spend,
    coalesce(s.total_impressions, 0)    as total_impressions,
    coalesce(s.total_clicks, 0)         as total_clicks,
    coalesce(s.avg_ctr, 0)             as avg_ctr,

    -- Order metrics
    coalesce(o.total_orders, 0)         as total_orders,
    round(cast(coalesce(o.total_revenue, 0) as numeric), 2)      as total_revenue,
    coalesce(o.avg_order_value, 0)      as avg_order_value,

    -- Calculated metrics
    case
        when coalesce(s.total_spend, 0) = 0 then 0
        else round(
            cast(coalesce(o.total_revenue, 0) as numeric) /
            cast(s.total_spend as numeric), 2
        )
    end                                 as roas,

    case
        when coalesce(s.total_clicks, 0) = 0 then 0
        else round(
            cast(coalesce(o.total_orders, 0) as numeric) /
            cast(s.total_clicks as numeric), 4
        )
    end                                 as conversion_rate,

    case
        when coalesce(s.total_spend, 0) = 0 then 0
        else round(
            cast(s.total_spend as numeric) /
            nullif(cast(coalesce(o.total_orders, 0) as numeric), 0), 2
        )
    end                                 as cost_per_order

from campaigns c
left join spend s on c.campaign_id = s.campaign_id
left join orders o on c.campaign_id = o.campaign_id