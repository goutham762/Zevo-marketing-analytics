

-- ============================================================
-- int_instagram_deterioration.sql
-- Instagram performance broken down by year
-- Proves the core finding:
-- 2023 — acceptable early results
-- 2024 — audience fatigue, spend increases, performance drops
-- ============================================================

with campaign_performance as (

    select * from "Zevo_analytics"."staging"."int_campaign_performance"

),

instagram_only as (

    select * from campaign_performance
    where channel_id = 'CH003'

)

select
    year,

    -- Campaign volume
    count(campaign_id)                              as total_campaigns,

    -- Spend
    round(sum(total_budget)::numeric, 2)            as total_budget,
    round(sum(total_spend)::numeric, 2)             as total_spend,

    -- Traffic
    sum(total_impressions)                          as total_impressions,
    sum(total_clicks)                               as total_clicks,
    round(avg(avg_ctr)::numeric, 4)                 as avg_ctr,

    -- Revenue
    sum(total_orders)                               as total_orders,
    round(sum(total_revenue)::numeric, 2)           as total_revenue,
    round(avg(avg_order_value)::numeric, 2)         as avg_order_value,

    -- Performance
    case
        when sum(total_spend) = 0 then 0
        else round(
            sum(total_revenue)::numeric /
            sum(total_spend)::numeric, 2
        )
    end                                             as roas,

    case
        when sum(total_clicks) = 0 then 0
        else round(
            sum(total_orders)::numeric /
            sum(total_clicks)::numeric, 4
        )
    end                                             as conversion_rate,

    case
        when sum(total_orders) = 0 then 0
        else round(
            sum(total_spend)::numeric /
            sum(total_orders)::numeric, 2
        )
    end                                             as cost_per_order

from instagram_only
group by year
order by year asc