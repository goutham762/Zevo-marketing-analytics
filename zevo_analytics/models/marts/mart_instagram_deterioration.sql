{{ config(
    materialized='table',
    schema='mart'
) }}
-- ============================================================
-- mart_instagram_deterioration.sql
-- Year over year Instagram performance comparison
-- Core finding table — proves the deterioration story
-- 2023: acceptable, 2024: loss making as spend scaled
-- ============================================================
with instagram_deterioration as (
    select * from {{ ref('int_instagram_deterioration') }}
)
select
    year,
    total_campaigns,
    total_budget,
    total_spend,
    total_impressions,
    total_clicks,
    round((avg_ctr * 100)::numeric, 2)      as avg_ctr_pct,
    total_orders,
    total_revenue,
    avg_order_value,
    roas,
    conversion_rate,
    cost_per_order,
    -- Year over year change labels for dashboard
    case
        when year = 2023 then 'Baseline Year'
        when year = 2024 then 'Deterioration Year'
    end                                         as year_label,
    -- ROAS verdict per year
    case
        when roas >= 1  then 'Profitable'
        else                 'Loss Making'
    end                                         as roas_verdict
from instagram_deterioration
order by year asc