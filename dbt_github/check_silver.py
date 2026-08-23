import glob
from google.cloud import bigquery

# Mencari file service account JSON di folder aktif maupun parent
key_files = glob.glob("*.json") + glob.glob("../*.json")
key_files = [f for f in key_files if any(k in f for k in ["key", "gcp", "data-engineer"])]

if not key_files:
    raise FileNotFoundError("File service account JSON tidak ditemukan.")

client = bigquery.Client.from_service_account_json(key_files[0])

queries = {
    "stg_repositories": "SELECT repo_id, full_name, stars_count, primary_language FROM `data-engineer-gcp-506208.data_silver.stg_repositories` LIMIT 3",
    "stg_commits": "SELECT repo_name, author_name, commit_date, SUBSTR(commit_message, 1, 40) AS message_preview FROM `data-engineer-gcp-506208.data_silver.stg_commits` LIMIT 3",
    "stg_pull_requests": "SELECT repo_name, pr_number, title, state, author_username, is_merged FROM `data-engineer-gcp-506208.data_silver.stg_pull_requests` LIMIT 3"
}

for table, sql in queries.items():
    print(f"\n{'='*20} SAMPEL {table.upper()} {'='*20}")
    for row in client.query(sql).result():
        print(dict(row))