
  
    

  create  table "Zevo_analytics"."mart"."mart_channel_roas__dbt_tmp"
  
  
    as
  
  (
    

-- ============================================================
-- mart_channel_roas.sql
-- Final channel performance table for Power BI
-- One row per channel — full 2 year picture
-- Channel names joined in for dashboard readability
-- This is the core finding table of the entire project
-- ============================================================

with channel_summary as (

    select * from "Zevo_analytics"."staging"."int_channel_summary"

),

channel_names as (

    select * from "Zevo_analytics"."staging"."stg_channels"

)

select
    n.channel_name,
    n.channel_type,
    s.total_campaigns,

    -- Budget vs spend
    s.total_budget,
    s.total_spend,
    round(
        (s.total_spend / nullif(s.total_budget, 0) * 100)::numeric, 1
    )                                           as budget_utilization_pct,

    -- Traffic metrics
    s.total_impressions,
    s.total_clicks,
    s.avg_ctr,

    -- Revenue metrics
    s.total_orders,
    s.total_revenue,
    s.avg_order_value,

    -- Performance metrics
    s.roas,
    s.conversion_rate,
    s.cost_per_order,

    -- Verdict column for dashboard
    case
        when s.roas >= 5    then 'Excellent'
        when s.roas >= 2    then 'Profitable'
        when s.roas >= 1    then 'Break Even'
        else                     'Loss Making'
    end                                         as performance_verdict

from channel_summary s
left join channel_names n on s.channel_id = n.channel_id
order by s.roas desc
  );
  