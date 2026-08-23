# 🚀 End-to-End GitHub Engineering Analytics Pipeline (GCP + dbt)

[![GCP](https://img.shields.io/badge/Google_Cloud-BigQuery-4285F4?style=flat-square&logo=googlecloud&logoColor=white)](https://cloud.google.com/bigquery)
[![dbt](https://img.shields.io/badge/dbt-Core_v1.12-FF694B?style=flat-square&logo=dbt&logoColor=white)](https://www.getdbt.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Looker Studio](https://img.shields.io/badge/Looker_Studio-BI_Dashboard-F9AB00?style=flat-square&logo=google&logoColor=white)](https://lookerstudio.google.com/)

An enterprise-grade ELT data pipeline that extracts software development metrics from the GitHub REST API, loads raw semi-structured JSON payloads into Google Cloud BigQuery, models and cleanses data using dbt (Data Build Tool) following the Medallion Architecture (Star Schema), and visualizes engineering velocity and repository health in Google Looker Studio.

---

## 🏗️ Architecture Overview

   mermaid
flowchart LR
    subgraph Ingestion_Layer [1. Ingestion Layer]
        API[GitHub REST API] -->|Python Extraction| BQ_Bronze[(BigQuery: Bronze\nRaw JSON Payloads)]
    end

    subgraph Transformation_Layer [2. Transformation Layer - dbt]
        BQ_Bronze -->|Staging & Deduplication| BQ_Silver[(BigQuery: Silver\nCleaned Views)]
        BQ_Silver -->|Star Schema & Aggregations| BQ_Gold[(BigQuery: Gold\nFact & Dimension Marts)]
    end

    subgraph Consumption_Layer [3. Consumption Layer]
        BQ_Gold -->|Direct Query| Looker[Looker Studio Dashboard]
    end
🛠️ Tech Stack & Technologies
Extraction & Ingestion: Python 3.12, GitHub REST API, Google Cloud BigQuery Client Library (google-cloud-bigquery).

Cloud Data Warehouse: Google Cloud BigQuery.

Data Transformation & Modeling: dbt Core (v1.12), SQL (Common Table Expressions / CTE, SAFE_CAST, JSON parsing).

Data Quality & Testing: dbt generic test suites (unique, not_null, relationships, accepted_values).

Business Intelligence / BI: Google Looker Studio.

Version Control & CI/CD: Git, GitHub.
```text
📂 Repository Structure
Plaintext
porto-data-engineer_1/
├── dbt_github/
│   ├── dbt_project.yml              # dbt core configuration
│   ├── packages.yml                 # dbt package dependencies
│   ├── models/
│   │   ├── staging/
│   │   │   ├── sources.yml          # Bronze layer source declarations
│   │   │   ├── schema.yml           # Staging data testing rules
│   │   │   ├── stg_repositories.sql # Repositories staging model
│   │   │   ├── stg_commits.sql      # Commits staging model
│   │   │   └── stg_pull_requests.sql# Pull requests staging model
│   │   └── marts/
│   │       ├── schema.yml           # Marts data integrity & foreign key tests
│   │       ├── dim_repositories.sql # Master repository dimension
│   │       ├── dim_authors.sql      # Unified developer & contributor dimension
│   │       ├── fct_commits.sql      # Commit activity fact table
│   │       ├── fct_pull_requests.sql# PR lifecycle and lead time fact table
│   │       └── mart_repository_overview.sql # Pre-aggregated analytical table
├── scripts/
│   ├── ingest_github.py             # Python ingestion script (API to BigQuery)
│   ├── check_silver.py              # Silver layer data sampling script
│   └── audit_gold.py                # Full-volume data quality audit script
├── assets/
│   ├── dbt_dag_lineage.png          # dbt lineage graph screenshot
│   └── dashboard_preview.png        # Looker Studio dashboard preview
├── .gitignore                       # Security rules (GCP keys & env ignore)
├── requirements.txt                 # Python dependencies
└── README.md                        # Project documentation

```
🔄 Data Pipeline Breakdown (Medallion Architecture)
1. Bronze Layer (data_bronze)
Raw Storage: Ingests raw JSON responses directly from GitHub REST API endpoints (/repos, /commits, /pulls).

Audit Trail: Preserves exact raw payloads with source timestamps (ingested_at) to enable point-in-time recovery and zero-loss ingestion.

2. Silver Layer (data_silver - Staging)
stg_repositories: Deduplicated repository metadata (stars, forks, open issues, primary language).

stg_commits: Flattened commit log with parsed author identity, commit messages, and UTC timestamps.

stg_pull_requests: Flattened PR lifecycle records with status indicators (is_merged, state, timestamps).

Engineering Standards:

Deduplication using ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ingested_at DESC).

Safe JSON scalar casting with SAFE_CAST() to prevent pipeline failures from unexpected schema drift.

3. Gold Layer (data_silver - Data Marts / Star Schema)
dim_repositories: Master repository dimension serving context to fact tables.

dim_authors: Unified contributor dimension combining commit authors and PR creators with generated MD5 surrogate keys (author_id).

fct_commits: Fact table capturing developer work patterns (commit hour, day of week, message length).

fct_pull_requests: Fact table computing engineering velocity metrics (resolution / lead time in hours).

mart_repository_overview: Pre-aggregated summary mart built for low-latency BI queries.

🔍 Data Lineage (dbt DAG)
The transformation pipeline is modular and fully decoupled across layers:

🧪 Data Testing & Quality Assurance
Data integrity is validated automatically via dbt generic tests:

Primary Key Uniqueness & Completeness: Tested on repo_id, commit_sha, pr_id, and author_id.

Referential Integrity (Foreign Keys): Validated relationships between fct_commits.repo_id / fct_pull_requests.repo_id and dim_repositories.repo_id.

Categorical Constraints: Enforced valid PR states (accepted_values: ['open', 'closed']).

Bash
dbt test
# Result: PASS=8 WARN=0 ERROR=0 TOTAL=8
📊 Analytical Insights & Looker Studio Dashboard
Key Metrics Tracked:
Engineering Velocity / PR Lead Time: Analysis of the average review-to-merge turnaround time across major open-source web frameworks (FastAPI, Gin, Django, NestJS, Laravel).

Repository Health & Popularity: Comparative analysis between GitHub Stars, Fork Velocity, and Open Issue ratios.

Developer Contribution Footprint: Contributor distribution tracking direct code pushes vs peer-reviewed pull requests.

🔗 Live Interactive Dashboard: View on Looker Studio

⚙️ How to Reproduce Locally
1. Clone Repository & Setup Environment
Bash
git clone [https://github.com/USERNAME/NAMA_REPO_KAMU.git](https://github.com/USERNAME/NAMA_REPO_KAMU.git)
cd NAMA_REPO_KAMU

python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
2. Configure GCP Authentication
Place your GCP Service Account JSON key (with BigQuery Admin / Data Editor permissions) into the root directory.

3. Run Data Ingestion (Bronze Layer)
Bash
python scripts/ingest_github.py
4. Run dbt Transformation & Quality Tests (Silver & Gold Layers)
Bash
cd dbt_github
dbt run
dbt test
5. Verify Gold Layer Data
Bash
python ../scripts/audit_gold.py
👤 Author
Portfolio Project by: [Nama Kamu]

LinkedIn: [Link LinkedIn Kamu]

GitHub: [Link GitHub Kamu]
