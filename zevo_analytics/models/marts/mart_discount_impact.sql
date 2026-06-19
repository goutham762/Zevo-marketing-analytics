{{ config(
    materialized='table',
    schema='mart'
) }}

-- ============================================================
-- mart_discount_impact.sql
-- Discount frequency and revenue impact per channel
-- Shows whether discounts are helping or hurting profitability
-- Key finding: Instagram discounts most but performs worst
-- ============================================================

with orders as (

    select * from {{ ref('stg_orders') }}

),

channel_names as (

    select * from {{ ref('stg_channels') }}

)

select
    o.channel_id,
    n.channel_name,
    o.year,

    -- Total orders
    count(o.order_id)                               as total_orders,

    -- Discounted vs full price orders
    sum(case when o.discount_applied then 1 else 0 end)
                                                    as discounted_orders,
    sum(case when not o.discount_applied then 1 else 0 end)
                                                    as full_price_orders,

    -- Discount rate
    round(
        sum(case when o.discount_applied then 1 else 0 end)::numeric /
        count(o.order_id)::numeric * 100, 1
    )                                               as discount_rate_pct,

    -- Revenue comparison
    round(avg(case when o.discount_applied
        then o.revenue end)::numeric, 2)            as avg_discounted_revenue,
    round(avg(case when not o.discount_applied
        then o.revenue end)::numeric, 2)            as avg_full_price_revenue,

    -- Total revenue
    round(sum(o.revenue)::numeric, 2)               as total_revenue,
    round(sum(case when o.discount_applied
        then o.revenue end)::numeric, 2)            as discounted_revenue,
    round(sum(case when not o.discount_applied
        then o.revenue end)::numeric, 2)            as full_price_revenue,

    -- Revenue loss from discounting
    round(
        (avg(case when not o.discount_applied then o.revenue end) -
         avg(case when o.discount_applied then o.revenue end))::numeric
    , 2)                                            as avg_revenue_loss_per_discount

from orders o
left join channel_names n on o.channel_id = n.channel_id
group by
    o.channel_id,
    n.channel_name,
    o.year
order by
    o.year asc,
    discount_rate_pct desc