with source as (
    select * from {{ source('bronze_github', 'raw_commits') }}
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
        json_value(payload_str, '$.sha') as commit_sha,
        coalesce(
            json_value(payload_str, '$.commit.author.name'),
            json_value(payload_str, '$.author.login'),
            'Unknown Author'
        ) as author_name,
        json_value(payload_str, '$.commit.author.email') as author_email,
        safe_cast(json_value(payload_str, '$.commit.author.date') as timestamp) as commit_date,
        json_value(payload_str, '$.commit.message') as commit_message,
        ingested_at,
        row_number() over(
            partition by json_value(payload_str, '$.sha')
            order by ingested_at desc
        ) as rn
    from unwrapped
)

select
    commit_sha,
    repo_name,
    author_name,
    author_email,
    commit_date,
    commit_message,
    ingested_at as staged_at
from parsed
where rn = 1
  and commit_sha is not null