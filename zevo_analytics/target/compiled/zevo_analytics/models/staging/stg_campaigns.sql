

-- ============================================================
-- stg_campaigns.sql
-- Staging model for campaigns table
-- Source: raw.campaigns
-- 136 rows — one per campaign
-- ============================================================

with source as (
    select * from "Zevo_analytics"."raw"."campaigns"
),
renamed as (
    select
        campaign_id,
        campaign_name,
        channel_id,
        year,
        start_date::date        as start_date,
        end_date::date          as end_date,
        total_budget,
        duration_days,
        start_month,
        start_quarter
    from source
)
select * from renamed