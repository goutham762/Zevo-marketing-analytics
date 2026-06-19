

-- ============================================================
-- stg_daily_spend.sql
-- Staging model for daily_spend table
-- Source: raw.daily_spend
-- 11,277 rows — daily spend per ad set per campaign
-- ============================================================

with source as (

    select * from "Zevo_analytics"."raw"."daily_spend"

),

renamed as (

    select
        spend_id,
        campaign_id,
        channel_id,
        ad_set_name,
        date::date              as spend_date,
        amount_spent,
        impressions,
        clicks,
        ctr,
        month,
        quarter,
        day_of_week,
        is_weekend,
        is_festival
    from source

)

select * from renamed