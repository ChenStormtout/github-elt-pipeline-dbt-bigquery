with source as (
    select * from {{ source('bronze_github', 'raw_pull_requests') }}
),

unwrapped as (
    select
        repo_name,
        ingested_at,
        string(raw_payload) as payload_str
    from source
),

parsed as (
    select
        repo_name,
        safe_cast(json_value(payload_str, '$.id') as int64) as pr_id,
        safe_cast(json_value(payload_str, '$.number') as int64) as pr_number,
        json_value(payload_str, '$.title') as title,
        json_value(payload_str, '$.state') as state,
        coalesce(json_value(payload_str, '$.user.login'), 'Unknown') as author_username,
        safe_cast(json_value(payload_str, '$.created_at') as timestamp) as created_at,
        safe_cast(json_value(payload_str, '$.updated_at') as timestamp) as updated_at,
        safe_cast(json_value(payload_str, '$.closed_at') as timestamp) as closed_at,
        safe_cast(json_value(payload_str, '$.merged_at') as timestamp) as merged_at,
        case 
            when json_value(payload_str, '$.merged_at') is not null then true 
            else false 
        end as is_merged,
        ingested_at,
        row_number() over(
            partition by safe_cast(json_value(payload_str, '$.id') as int64)
            order by ingested_at desc
        ) as rn
    from unwrapped
)

select
    pr_id,
    repo_name,
    pr_number,
    title,
    state,
    author_username,
    is_merged,
    created_at,
    updated_at,
    closed_at,
    merged_at,
    ingested_at as staged_at
from parsed
where rn = 1
  and pr_id is not null