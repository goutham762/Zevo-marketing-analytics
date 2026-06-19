

-- ============================================================
-- mart_campaign_performance.sql
-- Full campaign ranking — best to worst by ROAS
-- Exposes money wasting campaigns specifically
-- Powers campaign level analysis in Power BI
-- ============================================================

with campaign_performance as (

    select * from "Zevo_analytics"."staging"."int_campaign_performance"

),

channel_names as (

    select * from "Zevo_analytics"."staging"."stg_channels"

)

select
    cp.campaign_id,
    cp.campaign_name,
    n.channel_name,
    cp.year,
    cp.start_date,
    cp.end_date,
    cp.duration_days,
    cp.start_quarter,

    -- Budget vs spend
    cp.total_budget,
    cp.total_spend,
    round(
        (cp.total_spend / nullif(cp.total_budget, 0) * 100)::numeric, 1
    )                                           as budget_utilization_pct,

    -- Traffic metrics
    cp.total_impressions,
    cp.total_clicks,
    cp.avg_ctr,

    -- Revenue metrics
    cp.total_orders,
    cp.total_revenue,
    cp.avg_order_value,

    -- Performance metrics
    cp.roas,
    cp.conversion_rate,
    cp.cost_per_order,

    -- Performance verdict
    case
        when cp.roas >= 5   then 'Excellent'
        when cp.roas >= 2   then 'Profitable'
        when cp.roas >= 1   then 'Break Even'
        when cp.roas > 0    then 'Loss Making'
        else                     'No Revenue'
    end                                         as performance_verdict,

    -- Rank by ROAS within each year
    rank() over (
        partition by cp.year
        order by cp.roas desc
    )                                           as roas_rank_in_year

from campaign_performance cp
left join channel_names n on cp.channel_id = n.channel_id
order by cp.roas desc