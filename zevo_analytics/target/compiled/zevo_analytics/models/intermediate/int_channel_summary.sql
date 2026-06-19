

-- ============================================================
-- int_channel_summary.sql
-- Channel level aggregation of campaign performance
-- One row per channel showing full 2 year picture
-- Builds on int_campaign_performance
-- This is where the core ROAS story becomes visible
-- ============================================================

with campaign_performance as (

    select * from "Zevo_analytics"."staging"."int_campaign_performance"

)

select
    channel_id,

    -- Campaign counts
    count(campaign_id)                          as total_campaigns,

    -- Budget vs actual spend
    round(sum(total_budget)::numeric, 2)        as total_budget,
    round(sum(total_spend)::numeric, 2)         as total_spend,

    -- Traffic metrics
    sum(total_impressions)                      as total_impressions,
    sum(total_clicks)                           as total_clicks,
    round(avg(avg_ctr)::numeric, 4)             as avg_ctr,

    -- Revenue metrics
    sum(total_orders)                           as total_orders,
    round(sum(total_revenue)::numeric, 2)       as total_revenue,
    round(avg(avg_order_value)::numeric, 2)     as avg_order_value,

    -- Performance metrics
    case
        when sum(total_spend) = 0 then 0
        else round(
            sum(total_revenue)::numeric /
            sum(total_spend)::numeric, 2
        )
    end                                         as roas,

    case
        when sum(total_clicks) = 0 then 0
        else round(
            sum(total_orders)::numeric /
            sum(total_clicks)::numeric, 4
        )
    end                                         as conversion_rate,

    case
        when sum(total_orders) = 0 then 0
        else round(
            sum(total_spend)::numeric /
            sum(total_orders)::numeric, 2
        )
    end                                         as cost_per_order

from campaign_performance
group by channel_id
order by roas desc