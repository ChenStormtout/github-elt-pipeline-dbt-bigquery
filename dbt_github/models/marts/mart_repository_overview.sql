with repos as (
    select * from {{ ref('dim_repositories') }}
),

commits as (
    select 
        repo_id,
        count(*) as total_commits,
        count(distinct author_name) as distinct_committers,
        min(commit_date) as earliest_commit,
        max(commit_date) as latest_commit
    from {{ ref('fct_commits') }}
    group by repo_id
),

prs as (
    select 
        repo_id,
        count(*) as total_prs,
        countif(is_merged = true) as merged_prs_count,
        countif(state = 'open') as open_prs_count,
        round(avg(resolution_time_hours), 2) as avg_pr_resolution_hours
    from {{ ref('fct_pull_requests') }}
    group by repo_id
)

select
    r.repo_id,
    r.repo_name,
    r.full_name,
    r.owner_name,
    r.primary_language,
    r.stars_count,
    r.forks_count,
    r.open_issues_count,
    coalesce(c.total_commits, 0) as total_commits,
    coalesce(c.distinct_committers, 0) as distinct_committers,
    coalesce(p.total_prs, 0) as total_prs,
    coalesce(p.merged_prs_count, 0) as merged_prs_count,
    coalesce(p.open_prs_count, 0) as open_prs_count,
    coalesce(p.avg_pr_resolution_hours, 0.0) as avg_pr_resolution_hours,
    c.earliest_commit,
    c.latest_commit,
    current_timestamp() as mart_generated_at
from repos r
left join commits c on r.repo_id = c.repo_id
left join prs p on r.repo_id = p.repo_id