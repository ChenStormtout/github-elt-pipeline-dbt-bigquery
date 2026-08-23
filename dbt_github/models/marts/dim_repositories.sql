with repos as (
    select * from {{ ref('stg_repositories') }}
)

select
    repo_id,
    repo_name,
    full_name,
    owner_name,
    description,
    stars_count,
    forks_count,
    open_issues_count,
    primary_language,
    created_at,
    updated_at,
    staged_at
from repos