

-- ============================================================
-- int_daily_trends.sql
-- Daily spend and revenue trends across full 2 year period
-- Powers trend charts in Power BI dashboard
-- Shows seasonal spikes, festival periods, growth trajectory
-- ============================================================

with daily_spend as (

    select
        spend_date,
        channel_id,
        sum(amount_spent)       as daily_spend,
        sum(impressions)        as daily_impressions,
        sum(clicks)             as daily_clicks,
        avg(ctr)                as avg_ctr,
        max(is_weekend::int)    as is_weekend,
        max(is_festival::int)   as is_festival,
        month,
        quarter
    from "Zevo_analytics"."staging"."stg_daily_spend"
    group by spend_date, channel_id, month, quarter

),

daily_orders as (

    select
        order_date,
        channel_id,
        count(order_id)         as daily_orders,
        sum(revenue)            as daily_revenue
    from "Zevo_analytics"."staging"."stg_orders"
    group by order_date, channel_id

)

select
    s.spend_date                                        as date,
    s.channel_id,
    s.month,
    s.quarter,
    extract(year from s.spend_date)::int                as year,
    s.is_weekend::boolean                               as is_weekend,
    s.is_festival::boolean                              as is_festival,

    -- Spend metrics
    round(s.daily_spend::numeric, 2)                    as daily_spend,
    s.daily_impressions,
    s.daily_clicks,
    round(s.avg_ctr::numeric, 4)                        as avg_ctr,

    -- Revenue metrics
    coalesce(o.daily_orders, 0)                         as daily_orders,
    round(coalesce(o.daily_revenue, 0)::numeric, 2)     as daily_revenue,

    -- Daily ROAS
    case
        when s.daily_spend = 0 then 0
        else round(
            coalesce(o.daily_revenue, 0)::numeric /
            s.daily_spend::numeric, 2
        )
    end                                                 as daily_roas

from daily_spend s
left join daily_orders o
    on s.spend_date = o.order_date
    and s.channel_id = o.channel_id
order by s.spend_date, s.channel_id