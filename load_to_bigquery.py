import os
import glob
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from google.oauth2 import service_account

# 1. Load variabel dari .env
load_dotenv()

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
DATASET_ID = os.getenv("GCP_DATASET_ID", "data_bronze")
KEY_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "gcp-key.json")
LOCATION = "US"  # Sesuaikan dengan region dataset Anda

# 2. Inisialisasi Auth & Client BigQuery
if not os.path.exists(KEY_PATH):
    raise FileNotFoundError(f"File kredensial '{KEY_PATH}' tidak ditemukan di folder proyek!")

credentials = service_account.Credentials.from_service_account_file(KEY_PATH)
client = bigquery.Client(credentials=credentials, project=PROJECT_ID)

def create_dataset_if_not_exists():
    """Memastikan dataset Bronze sudah tersedia."""
    dataset_ref = bigquery.DatasetReference(PROJECT_ID, DATASET_ID)
    try:
        client.get_dataset(dataset_ref)
        print(f"[OK] Dataset `{DATASET_ID}` sudah ada.")
    except NotFound:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = LOCATION
        client.create_dataset(dataset, timeout=30)
        print(f"[CREATED] Dataset `{DATASET_ID}` berhasil dibuat.")

def get_or_create_table(table_name: str) -> bigquery.Table:
    """Membuat tabel Bronze dengan skema JSON jika belum ada."""
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
    
    schema = [
        bigquery.SchemaField("repo_name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("ingested_at", "TIMESTAMP", mode="REQUIRED"),
        bigquery.SchemaField("raw_payload", "JSON", mode="REQUIRED"),
    ]
    
    try:
        table = client.get_table(table_ref)
        return table
    except NotFound:
        table = bigquery.Table(table_ref, schema=schema)
        table = client.create_table(table)
        print(f"[CREATED] Tabel `{table_name}` berhasil dibuat.")
        return table

def load_json_files_to_bigquery():
    create_dataset_if_not_exists()
    
    entities = ["repositories", "commits", "pull_requests"]
    
    for entity in entities:
        table_name = f"raw_{entity}"
        table = get_or_create_table(table_name)
        table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
        
        pattern = os.path.join("data", "raw", entity, "*", "*.json")
        json_files = glob.glob(pattern)
        
        rows_to_insert = []
        now_ts = datetime.now(timezone.utc).isoformat()
        
        print(f"\nMemproses {len(json_files)} file untuk tabel `{table_name}`...")
        
        for file_path in json_files:
            file_name = os.path.basename(file_path).replace(".json", "")
            repo_name = file_name.replace("_", "/", 1)
            
            with open(file_path, "r", encoding="utf-8") as f:
                content = json.load(f)
                
            if isinstance(content, list):
                for item in content:
                    rows_to_insert.append({
                        "repo_name": repo_name,
                        "ingested_at": now_ts,
                        "raw_payload": json.dumps(item)  # Serialisasi string untuk kompatibilitas load job
                    })
            else:
                rows_to_insert.append({
                    "repo_name": repo_name,
                    "ingested_at": now_ts,
                    "raw_payload": json.dumps(content)
                })
        
        if rows_to_insert:
            # Gunakan Batch Load Job (Gratis di Free Tier / Sandbox)
            job_config = bigquery.LoadJobConfig(
                schema=table.schema,
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND
            )
            
            job = client.load_table_from_json(
                rows_to_insert, 
                table_ref, 
                job_config=job_config
            )
            job.result()  # Menunggu proses load selesai di BigQuery
            print(f"[SUCCESS] Berhasil memuat {len(rows_to_insert)} baris ke `{table_name}` via Batch Job")

if __name__ == "__main__":
    load_json_files_to_bigquery()