{{ config(schema='staging') }}

-- ============================================================
-- stg_orders.sql
-- Staging model for orders table
-- Source: raw.orders
-- 10,872 rows — one per order
-- ============================================================

with source as (

    select * from {{ source('raw', 'orders') }}

),

renamed as (

    select
        order_id,
        campaign_id,
        channel_id,
        order_date::date        as order_date,
        revenue,
        product_category,
        discount_applied,
        year,
        month,
        quarter,
        is_festival,
        revenue_bucket
    from source

)

select * from renamed