import glob
from google.cloud import bigquery

key_files = glob.glob("*.json") + glob.glob("../*.json")
key_files = [f for f in key_files if any(k in f for k in ["key", "gcp", "data-engineer"])]
client = bigquery.Client.from_service_account_json(key_files[0])

print("=" * 80)
print(" AUDIT FINAL: DATA GOLD LAYER (MARTS)")
print("=" * 80)

# Cek isi tabel ringkasan
query = """
    SELECT 
        repo_name, 
        primary_language, 
        stars_count, 
        total_commits, 
        total_prs, 
        merged_prs_count, 
        avg_pr_resolution_hours
    FROM `data-engineer-gcp-506208.data_silver.mart_repository_overview`
    ORDER BY stars_count DESC
"""

print(f"{'Repository':<25} | {'Lang':<8} | {'Stars':<8} | {'Commits':<8} | {'PRs':<6} | {'Merged':<6} | {'Avg Lead Time (Hrs)'}")
print("-" * 88)
for row in client.query(query).result():
    print(f"{row.repo_name:<25} | {str(row.primary_language):<8} | {row.stars_count:<8} | {row.total_commits:<8} | {row.total_prs:<6} | {row.merged_prs_count:<6} | {row.avg_pr_resolution_hours} hrs")

print("=" * 80)