with commits as (
    select * from {{ ref('stg_commits') }}
),

repos as (
    select repo_id, repo_name from {{ ref('stg_repositories') }}
)

select
    c.commit_sha,
    r.repo_id,
    c.repo_name,
    c.author_name,
    c.author_email,
    c.commit_date,
    date(c.commit_date) as commit_date_day,
    extract(hour from c.commit_date) as commit_hour,
    extract(dayofweek from c.commit_date) as commit_day_of_week,
    length(c.commit_message) as commit_message_length,
    c.commit_message,
    c.staged_at
from commits c
left join repos r on c.repo_name = r.repo_name