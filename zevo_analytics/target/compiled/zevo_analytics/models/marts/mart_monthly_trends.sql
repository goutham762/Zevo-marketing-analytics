

-- ============================================================
-- mart_monthly_trends.sql
-- Monthly aggregation of spend and revenue across 2 years
-- Powers trend charts in Power BI dashboard
-- Shows seasonal patterns, festival spikes, growth trajectory
-- ============================================================

with daily_trends as (

    select * from "Zevo_analytics"."staging"."int_daily_trends"

),

channel_names as (

    select * from "Zevo_analytics"."staging"."stg_channels"

)

select
    t.year,
    t.month,
    t.quarter,
    n.channel_name,
    t.channel_id,

    -- Spend metrics
    round(sum(t.daily_spend)::numeric, 2)           as monthly_spend,
    sum(t.daily_impressions)                        as monthly_impressions,
    sum(t.daily_clicks)                             as monthly_clicks,
    round(avg(t.avg_ctr)::numeric, 4)               as avg_ctr,

    -- Revenue metrics
    sum(t.daily_orders)                             as monthly_orders,
    round(sum(t.daily_revenue)::numeric, 2)         as monthly_revenue,

    -- Monthly ROAS
    case
        when sum(t.daily_spend) = 0 then 0
        else round(
            sum(t.daily_revenue)::numeric /
            sum(t.daily_spend)::numeric, 2
        )
    end                                             as monthly_roas,

    -- Festival and weekend flags
    max(t.is_festival::int)::boolean                as has_festival,
    max(t.is_weekend::int)::boolean                 as has_weekend

from daily_trends t
left join channel_names n on t.channel_id = n.channel_id
group by
    t.year,
    t.month,
    t.quarter,
    t.channel_id,
    n.channel_name
order by
    t.year asc,
    t.month asc,
    t.channel_id asc