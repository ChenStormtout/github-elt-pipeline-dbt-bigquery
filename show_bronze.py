import glob
from google.cloud import bigquery

# 1. Ambil Service Account JSON
key_files = glob.glob("*.json") + glob.glob("../*.json")
key_files = [f for f in key_files if any(k in f for k in ["key", "gcp", "data-engineer"])]

if not key_files:
    print("[ERROR] Service account JSON tidak ditemukan.")
    exit(1)

client = bigquery.Client.from_service_account_json(key_files[0])
project_id = client.project
dataset_id = "data_bronze"

print("=" * 80)
print(f" DAFTAR SEMUA TABEL & SKEMA DATASET: `{project_id}.{dataset_id}`")
print("=" * 80)

# 2. Query Metadata Kolom dari INFORMATION_SCHEMA
schema_query = f"""
    SELECT 
        table_name, 
        column_name, 
        data_type, 
        is_nullable
    FROM `{project_id}.{dataset_id}.INFORMATION_SCHEMA.COLUMNS`
    ORDER BY table_name, ordinal_position
"""
columns_meta = list(client.query(schema_query).result())
tables = sorted(list(set(r.table_name for r in columns_meta)))

if not tables:
    print(f"Tidak ada tabel ditemukan di dataset `{dataset_id}`.")
    exit(0)

# 3. Iterasi Setiap Tabel: Tampilkan Skema, Jumlah Baris, dan Sampel Data
for table in tables:
    print(f"\n📂 TABEL: {table}")
    print("-" * 60)
    
    # Cetak Struktur Kolom
    print("  [Daftar Kolom]")
    for col in columns_meta:
        if col.table_name == table:
            print(f"    • {col.column_name:<20} : {col.data_type:<15} (Nullable: {col.is_nullable})")
    
    # Hitung Jumlah Baris
    cnt_query = f"SELECT COUNT(*) AS total_rows FROM `{project_id}.{dataset_id}.{table}`"
    total_rows = list(client.query(cnt_query).result())[0].total_rows
    print(f"\n  [Total Baris]: {total_rows}")

    # Ambil 1 Baris Sampel Asli
    sample_query = f"SELECT * FROM `{project_id}.{dataset_id}.{table}` LIMIT 1"
    sample_rows = list(client.query(sample_query).result())
    if sample_rows:
        print("\n  [Sampel Data Baris Pertama]:")
        for k, v in dict(sample_rows[0]).items():
            val_str = str(v)
            if len(val_str) > 120:
                val_str = val_str[:120] + "... (truncated)"
            print(f"    - {k:<15}: {val_str}")
    print("-" * 60)

print("\n" + "=" * 80)
print(" INSPEKSI SELESAI")
print("=" * 80)