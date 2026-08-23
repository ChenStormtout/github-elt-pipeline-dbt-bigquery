with source as (
    select * from {{ source('bronze_github', 'raw_repositories') }}
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
        safe_cast(json_value(payload_str, '$.id') as int64) as repo_id,
        json_value(payload_str, '$.name') as repository_name,
        coalesce(json_value(payload_str, '$.full_name'), repo_name) as full_name,
        coalesce(json_value(payload_str, '$.owner.login'), 'Unknown') as owner_name,
        json_value(payload_str, '$.description') as description,
        safe_cast(json_value(payload_str, '$.stargazers_count') as int64) as stars_count,
        safe_cast(json_value(payload_str, '$.forks_count') as int64) as forks_count,
        safe_cast(json_value(payload_str, '$.open_issues_count') as int64) as open_issues_count,
        json_value(payload_str, '$.language') as primary_language,
        safe_cast(json_value(payload_str, '$.created_at') as timestamp) as created_at,
        safe_cast(json_value(payload_str, '$.updated_at') as timestamp) as updated_at,
        ingested_at,
        row_number() over(
            partition by repo_name 
            order by ingested_at desc
        ) as rn
    from unwrapped
)

select
    repo_id,
    repo_name,
    repository_name,
    full_name,
    owner_name,
    description,
    stars_count,
    forks_count,
    open_issues_count,
    primary_language,
    created_at,
    updated_at,
    ingested_at as staged_at
from parsed
where rn = 1
  and repo_id is not null