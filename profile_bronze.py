import glob
import json
from google.cloud import bigquery

# 1. Inisialisasi BigQuery Client
key_files = [f for f in glob.glob("*.json") if "gcp" in f or "data-engineer" in f or "key" in f]
if not key_files:
    raise FileNotFoundError("File service account JSON tidak ditemukan di direktori utama.")

client = bigquery.Client.from_service_account_json(key_files[0])
project_id = client.project
dataset_id = "data_bronze"

tables = ["raw_repositories", "raw_commits", "raw_pull_requests"]

print("=" * 75)
print(f" DATA PROFILING REPORT: `{project_id}.{dataset_id}`")
print("=" * 75)

for table_name in tables:
    table_ref = client.get_table(f"{project_id}.{dataset_id}.{table_name}")
    full_table = f"`{project_id}.{dataset_id}.{table_name}`"
    
    print(f"\n Profiling Tabel: {table_name}")
    print("-" * 55)
    
    # 1. Cek Skema Kolom & Tipe Data
    print("Daftar Kolom & Tipe Data:")
    for field in table_ref.schema:
        print(f"  • {field.name:<20} : {field.field_type} ({field.mode})")
    
    # 2. Cek Total Baris & Baris Null
    check_query = f"""
        SELECT 
            COUNT(*) AS total_rows,
            COUNTIF(raw_payload IS NULL) AS null_payload_rows,
            COUNT(DISTINCT repo_name) AS unique_repos
        FROM {full_table}
    """
    stats = list(client.query(check_query).result())[0]
    print(f"\nTotal Baris               : {stats.total_rows}")
    print(f"Jumlah Repositori Unik    : {stats.unique_repos}")
    print(f"Baris Payload NULL        : {stats.null_payload_rows}")

    # 3. Inspeksi Struktur Payload JSON (Sample 1 Baris Valid)
    sample_query = f"""
        SELECT 
            repo_name, 
            TO_JSON_STRING(raw_payload) AS payload_str
        FROM {full_table}
        WHERE raw_payload IS NOT NULL
        LIMIT 1
    """
    sample_rows = list(client.query(sample_query).result())
    
    if sample_rows:
        sample = sample_rows[0]
        try:
            parsed_json = json.loads(sample.payload_str)
            json_type = type(parsed_json).__name__
            print(f"Tipe Data JSON Root       : {json_type}")
            
            # Jika Root adalah List/Array
            if isinstance(parsed_json, list):
                print(f"Panjang Array Root        : {len(parsed_json)} item")
                if len(parsed_json) > 0:
                    first_item = parsed_json[0]
                    print(f"Tipe Item Pertama         : {type(first_item).__name__}")
                    if isinstance(first_item, dict):
                        print(f"Keys di Index [0]         : {list(first_item.keys())[:12]}")
            
            # Jika Root adalah Dict/Object
            elif isinstance(parsed_json, dict):
                print(f"Keys di Root JSON         : {list(parsed_json.keys())[:12]}")
                if "commit" in parsed_json and isinstance(parsed_json["commit"], dict):
                    print(f"  └─ Keys di `commit`     : {list(parsed_json['commit'].keys())}")
                    if "author" in parsed_json["commit"]:
                        print(f"     └─ `commit.author`   : {parsed_json['commit']['author']}")
                if "user" in parsed_json and isinstance(parsed_json["user"], dict):
                    print(f"  └─ `user` (Author PR)   : {parsed_json['user'].get('login')}")

        except Exception as e:
            print(f"[ERROR] Gagal parsing JSON: {e}")
    else:
        print("[WARNING] Tidak ada baris payload yang valid.")

print("\n" + "=" * 75)
print(" PROFILING SELESAI")
print("=" * 75)