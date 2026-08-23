import os
import json
import time
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "DE-Portfolio-Ingestion-Pipeline"
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"

REPOSITORIES = [
    "laravel/framework",
    "tiangolo/fastapi",
    "nestjs/nest",
    "django/django",
    "gin-gonic/gin"
]

def make_request(url: str, params: dict = None) -> list | dict:
    """Mengirim request dengan exponential backoff jika terkena rate limit."""
    response = requests.get(url, headers=HEADERS, params=params)
    
    if response.status_code == 403 and "rate limit" in response.text.lower():
        reset_time = int(response.headers.get("X-RateLimit-Reset", time.time() + 60))
        sleep_sec = max(reset_time - int(time.time()), 1)
        print(f"[WARN] Rate limit tercapai. Menunggu {sleep_sec} detik...")
        time.sleep(sleep_sec)
        response = requests.get(url, headers=HEADERS, params=params)

    response.raise_for_status()
    return response.json()

def save_raw_json(data: list | dict, entity: str, repo_name: str):
    """Menyimpan data mentah ke folder berpartisi tanggal."""
    today = datetime.now().strftime("%Y-%m-%d")
    sanitized_repo = repo_name.replace("/", "_")
    output_dir = os.path.join("data", "raw", entity, f"ingestion_date={today}")
    os.makedirs(output_dir, exist_ok=True)
    
    file_path = os.path.join(output_dir, f"{sanitized_repo}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  [SAVED] {file_path} ({len(data) if isinstance(data, list) else 1} records)")

def run_ingestion():
    print("=== MEMULAI INGESTION PIPELINE (BRONZE DUMP) ===")
    
    for repo in REPOSITORIES:
        print(f"\nProcessing: {repo}")
        
        # 1. Repo Metadata
        repo_data = make_request(f"https://api.github.com/repos/{repo}")
        save_raw_json(repo_data, "repositories", repo)
        
        # 2. Recent Commits (Ambil 200 commit terakhir)
        commits_data = make_request(
            f"https://api.github.com/repos/{repo}/commits", 
            params={"per_page": 200}
        )
        save_raw_json(commits_data, "commits", repo)
        
        # 3. Recent Pull Requests (Ambil 200 PR terakhir: open, closed, merged)
        prs_data = make_request(
            f"https://api.github.com/repos/{repo}/pulls", 
            params={"state": "all", "per_page": 200}
        )
        save_raw_json(prs_data, "pull_requests", repo)

    # Cek sisa kuota setelah pipeline selesai
    rate_info = make_request("https://api.github.com/rate_limit")
    core = rate_info.get("resources", {}).get("core", {})
    print(f"\n[DONE] Pipeline Selesai! Sisa Kuota API: {core.get('remaining')}/{core.get('limit')}")

if __name__ == "__main__":
    run_ingestion()