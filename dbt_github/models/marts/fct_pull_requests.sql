with prs as (
    select * from {{ ref('stg_pull_requests') }}
),

repos as (
    select repo_id, repo_name from {{ ref('stg_repositories') }}
)

select
    p.pr_id,
    r.repo_id,
    p.repo_name,
    p.pr_number,
    p.title,
    p.state,
    p.author_username,
    p.is_merged,
    p.created_at,
    p.updated_at,
    p.closed_at,
    p.merged_at,
    case 
        when p.merged_at is not null then timestamp_diff(p.merged_at, p.created_at, hour)
        when p.closed_at is not null then timestamp_diff(p.closed_at, p.created_at, hour)
        else null
    end as resolution_time_hours,
    p.staged_at
from prs p
left join repos r on p.repo_name = r.repo_name