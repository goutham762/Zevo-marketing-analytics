
  create view "Zevo_analytics"."staging"."stg_channels__dbt_tmp"
    
    
  as (
    
-- ============================================================
-- stg_channels.sql
-- Staging model for channels table
-- Source: raw.channels
-- 4 rows — one per marketing channel
-- ============================================================

with source as (

    select * from "Zevo_analytics"."raw"."channels"

),

renamed as (

    select
        channel_id,
        channel_name,
        channel_type
    from source

)

select * from renamed
  );