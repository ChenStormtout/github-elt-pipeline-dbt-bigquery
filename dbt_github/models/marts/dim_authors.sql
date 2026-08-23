with commit_authors as (
    select
        author_name,
        max(author_email) as author_email,
        count(*) as total_commits,
        min(commit_date) as first_commit_at,
        max(commit_date) as last_commit_at
    from {{ ref('stg_commits') }}
    where author_name is not null and author_name != 'Unknown Author'
    group by author_name
),

pr_authors as (
    select
        author_username as author_name,
        count(*) as total_prs,
        min(created_at) as first_pr_at,
        max(created_at) as last_pr_at
    from {{ ref('stg_pull_requests') }}
    where author_username is not null and author_username != 'Unknown'
    group by author_username
),

combined as (
    select
        coalesce(c.author_name, p.author_name) as author_name,
        c.author_email,
        coalesce(c.total_commits, 0) as total_commits,
        coalesce(p.total_prs, 0) as total_prs,
        coalesce(c.total_commits, 0) + coalesce(p.total_prs, 0) as total_contributions,
        c.first_commit_at,
        c.last_commit_at,
        p.first_pr_at,
        p.last_pr_at
    from commit_authors c
    full outer join pr_authors p on c.author_name = p.author_name
)

select
    to_hex(md5(author_name)) as author_id,
    author_name,
    author_email,
    total_commits,
    total_prs,
    total_contributions,
    first_commit_at,
    last_commit_at,
    first_pr_at,
    last_pr_at,
    current_timestamp() as mart_created_at
from combined