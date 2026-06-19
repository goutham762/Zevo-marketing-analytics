

-- ============================================================
-- scenario_reallocation.sql
-- 90-day budget reallocation test projection
-- Reduce Instagram by 30%, redirect to Google 60% Email 40%
-- THIS IS A PROJECTION — not actual business data
-- Assumptions: ROAS stable at higher spend levels
-- ============================================================

with channel_roas as (

    select
        max(case when channel_name = 'Instagram'
            then total_spend end)           as instagram_total_spend,
        max(case when channel_name = 'Instagram'
            then roas end)                  as instagram_roas,
        max(case when channel_name = 'Google Ads'
            then total_spend end)           as google_total_spend,
        max(case when channel_name = 'Google Ads'
            then roas end)                  as google_roas,
        max(case when channel_name = 'Email'
            then total_spend end)           as email_total_spend,
        max(case when channel_name = 'Email'
            then roas end)                  as email_roas,
        max(case when channel_name = 'Meta'
            then total_spend end)           as meta_total_spend
    from mart.mart_channel_roas

),

instagram_90day as (

    select
        *,
        round((instagram_total_spend / 24 * 3)::numeric, 2)
                                            as instagram_90day_spend
    from channel_roas

),

freed_budget as (

    select
        *,
        round((instagram_90day_spend * 0.30)::numeric, 2)
                                            as freed_budget,
        round((instagram_90day_spend * 0.30 * 0.60)::numeric, 2)
                                            as google_additional_spend,
        round((instagram_90day_spend * 0.30 * 0.40)::numeric, 2)
                                            as email_additional_spend
    from instagram_90day

)

select
    -- Scenario parameters
    0.30                                    as instagram_reduction_pct,
    0.60                                    as google_allocation_pct,
    0.40                                    as email_allocation_pct,
    90                                      as test_duration_days,

    -- Current spend by channel (actual, full 2 year period)
    google_total_spend                      as google_current_spend,
    meta_total_spend                        as meta_current_spend,
    instagram_total_spend                   as instagram_current_spend,
    email_total_spend                       as email_current_spend,

    -- Proposed spend by channel (after reallocation)
    round((google_total_spend + google_additional_spend)::numeric, 2)
                                            as google_proposed_spend,
    meta_total_spend                        as meta_proposed_spend,
    round((instagram_total_spend - freed_budget)::numeric, 2)
                                            as instagram_proposed_spend,
    round((email_total_spend + email_additional_spend)::numeric, 2)
                                            as email_proposed_spend,

    -- 90 day specific figures
    instagram_90day_spend                   as instagram_90day_spend,
    freed_budget                            as budget_freed,
    google_additional_spend                 as google_extra_spend,
    email_additional_spend                  as email_extra_spend,

    -- Revenue projections
    round((google_additional_spend * google_roas)::numeric, 2)
                                            as google_projected_revenue,
    round((email_additional_spend * email_roas)::numeric, 2)
                                            as email_projected_revenue,
    round((freed_budget * instagram_roas)::numeric, 2)
                                            as instagram_lost_revenue,

    -- Net impact
    round((
        (google_additional_spend * google_roas) +
        (email_additional_spend * email_roas) -
        (freed_budget * instagram_roas)
    )::numeric, 2)                          as net_revenue_gain_90days,

    -- Cost of inaction
    round((
        instagram_90day_spend -
        (instagram_90day_spend * instagram_roas)
    )::numeric, 2)                          as cost_of_inaction_90days

from freed_budget