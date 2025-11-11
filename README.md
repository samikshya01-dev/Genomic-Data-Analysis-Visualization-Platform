# Genomic Data Analysis & Visualization Platform

A comprehensive Python-MySQL-Power BI pipeline for analyzing genomic variant data from public VCF sources, enriching with clinical annotations, and visualizing insights.

## 🎯 Project Overview

This platform ingests genomic variant data from Ensembl, processes and normalizes it, enriches with clinical drug/biomarker data, stores in MySQL, and enables visualization through Power BI dashboards.

### Key Features

- **ETL Pipeline**: Automated extraction, transformation, and loading of VCF data
- **Clinical Enrichment**: Integration with DrugBank and ClinVar for drug-response metadata
- **Relational Storage**: Optimized MySQL schema for variant-level genomic data
- **Analytics**: Mutation frequency analysis, variant significance metrics
- **Visualization Ready**: Pre-aggregated data for Power BI dashboards

## 📋 Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Pipeline Phases](#pipeline-phases)
- [Database Schema](#database-schema)
- [Power BI Integration](#power-bi-integration)
- [Testing](#testing)
- [Contributing](#contributing)

## 🚀 Installation

### Prerequisites

- Python 3.11 or higher
- MySQL 8.0 or higher
- Power BI Desktop (for visualization)

### Setup Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd "Genomic Data Analysis Visualization Platform"
```

2. **Create and activate virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure MySQL Database**

Create a MySQL database:
```sql
CREATE DATABASE genomic_analysis CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

5. **Update Configuration Files**

Edit `config/db_config.yml`:
```yaml
database:
  host: localhost
  port: 3306
  database: genomic_analysis
  user: root
  password: your_password  # Update with your MySQL password
```

6. **Verify Setup**
```bash
python scripts/setup/verify_setup.py
```

For detailed setup instructions, see [docs/QUICKSTART.md](docs/QUICKSTART.md).

## ⚡ Quick Start

Run the complete pipeline with one command:

```bash
# Process 50,000 variants (recommended for first run)
./run_project.sh medium

# Or use the interactive script
./scripts/utilities/run_pipeline_now.sh
```

This will:
1. Download VCF data from Ensembl
2. Parse and transform variants
3. Enrich with gene/drug annotations
4. Load into MySQL database
5. Generate analysis reports

**Verify database:**
```bash
./scripts/utilities/verify_database.sh
```

For more options, see [docs/RUN_PROJECT_GUIDE.md](docs/RUN_PROJECT_GUIDE.md).

## ⚙️ Configuration

All configuration files are in the `config/` directory.

### Database Configuration (`config/db_config.yml`)

- Connection settings (host, port, database name, credentials)
- Connection pool configuration
- Performance tuning parameters
- Table naming conventions

### ETL Configuration (`config/etl_config.yml`)

- Data source URLs (Ensembl, DrugBank, ClinVar)
- File paths for raw and processed data
- VCF parsing configuration
- Processing parameters (chunk size, workers)
- Enrichment settings (gene mapping, drug annotations)
- Logging configuration

See the [Configuration Guide](docs/QUICK_REFERENCE.md#configuration) for detailed options.

## 📖 Usage

### Command-Line Interface

The main pipeline can be run in several modes:

#### Run Full Pipeline
```bash
python src/main.py --full
```

#### Run Individual Phases
```bash
# Extract VCF data
python src/main.py --extract

# Transform VCF to structured format
python src/main.py --transform

# Enrich with annotations
python src/main.py --enrich

# Load to MySQL
python src/main.py --load

# Generate analysis reports
python src/main.py --analyze
```

#### Advanced Options
```bash
# Process limited rows (for testing)
python src/main.py --full --max-rows 10000

# Force re-download and drop existing tables
python src/main.py --full --force-download --drop-existing

# Skip enrichment phase
python src/main.py --full --skip-enrichment

# Use vcfpy library for parsing (slower but more robust)
python src/main.py --transform --use-vcfpy
```

### Programmatic Usage

```python
from src.main import GenomicPipeline

# Create pipeline instance
pipeline = GenomicPipeline()

# Run full pipeline
pipeline.run_full_pipeline(
    force_download=False,
    max_rows=None,
    drop_existing=False,
    skip_enrichment=False,
    skip_analysis=False
)

# Or run individual phases
pipeline.run_extraction()
pipeline.run_transformation(max_rows=10000)
pipeline.run_enrichment()
pipeline.run_loading()
pipeline.run_analysis()
```

## 📁 Project Structure

```
Genomic Data Analysis Visualization Platform/
├── config/              # Configuration files
│   ├── db_config.yml
│   └── etl_config.yml
├── data/               # Data directory (gitignored)
│   ├── raw/           # Raw VCF files
│   ├── processed/     # Processed CSV files
│   └── logs/          # Application logs
├── src/               # Source code
│   ├── main.py       # Pipeline orchestrator
│   ├── etl/          # ETL modules
│   ├── analysis/     # Analysis modules
│   └── utils/        # Utility functions
├── scripts/          # Utility scripts
│   ├── utilities/    # Database and pipeline utilities
│   └── setup/        # Setup verification
├── docs/            # Documentation
│   ├── architecture/
│   ├── interview/
│   ├── technology/
│   └── fixes/
├── tests/           # Test suite
├── powerbi/         # Power BI resources
└── PROJECT_STRUCTURE.md  # Detailed structure guide
```

For complete file organization details, see [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md).

## 📚 Documentation

All documentation is organized in the `docs/` directory:

- **[Quick Start](docs/QUICKSTART.md)** - Get up and running in 5 minutes
- **[Run Guide](docs/RUN_PROJECT_GUIDE.md)** - Comprehensive pipeline execution guide
- **[Quick Reference](docs/QUICK_REFERENCE.md)** - Command cheat sheet
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions
- **[Architecture](docs/architecture/SYSTEM_ARCHITECTURE.md)** - System design
- **[Technology Stack](docs/technology/TECHNOLOGY_STACK.md)** - Technologies used
- **[Interview Prep](docs/interview/)** - Interview and presentation guides
- **[Power BI Setup](powerbi/POWERBI_GUIDE.md)** - Visualization guide

See [docs/README.md](docs/README.md) for the complete documentation index.

## 🗄️ Database Status

After running the pipeline, your MySQL database will contain:

| Table | Description | Typical Rows |
|-------|-------------|--------------|
| **variants** | Genomic variants from VCF | ~50,000+ |
| **genes** | Gene information and descriptions | ~10-200 |
| **drug_annotations** | Pharmacogenomic drug-gene associations | ~10 |
| **mutation_summary** | Aggregated statistics by gene/chromosome | ~100+ |

**Verify database:**
```bash
./scripts/utilities/verify_database.sh
```

**Connect to Power BI:**
- Server: `localhost`
- Database: `genomic_analysis`
- Port: `3306`
- Username: `root`
- Password: (your MySQL password)

## 🛠️ Utility Scripts

Helper scripts are organized in `scripts/`:

```bash
# Verify database status
./scripts/utilities/verify_database.sh

# Interactive pipeline runner
./scripts/utilities/run_pipeline_now.sh

# Populate sample gene/drug data
python scripts/utilities/populate_sample_data.py

# Fix database issues
python scripts/utilities/fix_database.py

# Verify setup and dependencies
python scripts/setup/verify_setup.py
```

See [scripts/README.md](scripts/README.md) for details.
genomic-platform/
│
├── data/
│   ├── raw/                     # Original VCF downloads
│   ├── processed/               # Cleaned CSVs and reports
│   └── logs/                    # ETL run logs
│
├── src/
│   ├── etl/
│   │   ├── extract_vcf.py       # Download & decompress VCF
│   │   ├── transform_vcf.py     # Parse and normalize variants
│   │   ├── load_to_mysql.py     # Insert into MySQL
│   │   └── enrich_annotations.py# Integrate clinical data
│   │
│   ├── analysis/
│   │   ├── variant_summary.py   # Aggregate statistics
│   │   └── mutation_analysis.py # Frequency & distribution
│   │
│   ├── utils/
│   │   ├── db_config.py         # MySQL connector setup
│   │   ├── logger.py            # Centralized logging
│   │   └── file_utils.py        # File operations
│   │
│   └── main.py                  # Pipeline orchestrator
│
├── config/
│   ├── db_config.yml            # Database configuration
│   └── etl_config.yml           # ETL configuration
│
├── powerbi/
│   └── genomic_dashboard.pbix   # Power BI report (to be created)
│
├── tests/
│   ├── test_vcf_parser.py
│   ├── test_db_inserts.py
│   └── test_data_quality.py
│
├── requirements.txt
├── README.md
└── setup.py
```

## 🔄 Pipeline Phases

### 1. Extraction
- Downloads VCF file from Ensembl FTP
- Decompresses .gz files
- Validates file integrity

### 2. Transformation
- Parses VCF format
- Extracts INFO fields (AF, AC, AN, CLNSIG, etc.)
- Maps variants to genes
- Normalizes clinical significance
- Outputs structured CSVs

### 3. Enrichment
- Queries Ensembl API for gene information
- Adds drug-response annotations
- Integrates clinical metadata
- Creates drug-gene association tables

### 4. Loading
- Creates MySQL database schema
- Bulk inserts variant data
- Loads gene and drug annotation tables
- Creates aggregated summary tables
- Builds indexes for performance

### 5. Analysis
- Generates mutation frequency statistics
- Analyzes clinical significance distribution
- Identifies top pathogenic variants
- Creates drug-biomarker associations
- Exports reports and visualizations

## 🗄️ Database Schema

### Tables

#### `variants`
Core variant information with genomic coordinates and clinical significance.

```sql
- id (INT, PK)
- chromosome (VARCHAR)
- position (INT)
- variant_id (VARCHAR)
- reference_allele (VARCHAR)
- alternate_allele (VARCHAR)
- quality (FLOAT)
- filter (VARCHAR)
- allele_frequency (FLOAT)
- allele_count (INT)
- total_alleles (INT)
- clinical_significance (VARCHAR)
- disease_name (TEXT)
- gene_symbol (VARCHAR)
- gene_id (VARCHAR)
- info_raw (TEXT)
```

#### `genes`
Unique gene information.

```sql
- id (INT, PK)
- gene_symbol (VARCHAR, UNIQUE)
- gene_id (VARCHAR)
- chromosome (VARCHAR)
- description (TEXT)
```

#### `drug_annotations`
Drug-gene associations and pharmacogenomic data.

```sql
- id (INT, PK)
- gene_symbol (VARCHAR)
- drug_name (VARCHAR)
- drug_bank_id (VARCHAR)
- mechanism (TEXT)
- indication (TEXT)
- drug_response (VARCHAR)
- adverse_effects (TEXT)
- clinical_trials (TEXT)
- source (VARCHAR)
```

#### `mutation_summary`
Pre-aggregated statistics for analytics and visualization.

```sql
- id (INT, PK)
- chromosome (VARCHAR)
- gene_symbol (VARCHAR)
- clinical_significance (VARCHAR)
- variant_count (INT)
- avg_allele_frequency (FLOAT)
- pathogenic_count (INT)
- benign_count (INT)
- drug_associated_count (INT)
```

### Indexes

Optimized indexes for common query patterns:
- Composite index on (chromosome, position)
- Index on gene_symbol
- Index on clinical_significance
- Composite index on (gene_symbol, clinical_significance)

## 📊 Power BI Integration

### Connecting to MySQL

1. Open Power BI Desktop
2. Get Data → MySQL Database
3. Enter server and database name
4. Import tables: `variants`, `genes`, `drug_annotations`, `mutation_summary`

### Recommended Visualizations

1. **Mutation Frequency Dashboard**
   - Bar chart: Variants by chromosome
   - Pie chart: Clinical significance distribution
   - Table: Top genes by variant count

2. **Drug-Biomarker Dashboard**
   - Network diagram: Gene-drug associations
   - Scatter plot: Allele frequency vs pathogenicity
   - Table: Drug responses by gene

3. **Clinical Significance Dashboard**
   - Stacked bar: Pathogenic vs benign by gene
   - Heat map: Mutation density across genome
   - Line chart: Variant frequency trends

### Sample DAX Measures

```dax
// Total Variants
Total Variants = COUNT(variants[id])

// Pathogenic Variant Rate
Pathogenic Rate = 
DIVIDE(
    COUNTROWS(FILTER(variants, variants[clinical_significance] = "Pathogenic")),
    COUNTROWS(variants)
)

// Average Allele Frequency
Avg AF = AVERAGE(variants[allele_frequency])

// Genes with Drug Targets
Genes With Drugs = DISTINCTCOUNT(drug_annotations[gene_symbol])
```

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test Suite
```bash
pytest tests/test_vcf_parser.py -v
pytest tests/test_db_inserts.py -v
pytest tests/test_data_quality.py -v
```

### Test Coverage
```bash
pytest --cov=src tests/
```

## 📈 Performance Optimization

### For Large Datasets

1. **Increase batch size** in `config/etl_config.yml`:
```yaml
processing:
  chunk_size: 100000
```

2. **Use parallel processing**:
```yaml
processing:
  max_workers: 8
```

3. **Optimize MySQL**:
```yaml
database:
  pool_size: 20
  max_overflow: 40
```

4. **Process specific chromosomes**:
Modify VCF URL to download specific chromosomes instead of full genome.

## 🔧 Troubleshooting

### Common Issues

**Issue**: MySQL connection fails
- **Solution**: Verify MySQL is running and credentials are correct in `config/db_config.yml`

**Issue**: VCF download is slow
- **Solution**: Download manually and place in `data/raw/` directory

**Issue**: Memory error during processing
- **Solution**: Reduce `chunk_size` in config or use `--max-rows` option

**Issue**: vcfpy parsing fails
- **Solution**: Use `--use-vcfpy` flag for more robust parsing

## 📝 Logging

Logs are stored in `data/logs/` with daily rotation. Log levels can be configured in `config/etl_config.yml`:

```yaml
logging:
  level: INFO  # DEBUG, INFO, WARNING, ERROR
  file_rotation: daily
  max_log_size_mb: 100
  backup_count: 7
```

## 🔄 Automation

### Schedule with Cron (Unix/Linux/macOS)

```bash
# Edit crontab
crontab -e

# Run every Sunday at 2 AM
0 2 * * 0 cd /path/to/project && /path/to/.venv/bin/python src/main.py --full >> logs/cron.log 2>&1
```

### Schedule with Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., weekly)
4. Action: Start a program
   - Program: `C:\path\to\.venv\Scripts\python.exe`
   - Arguments: `src/main.py --full`
   - Start in: `C:\path\to\project`

## 📚 References

- [Ensembl VCF Documentation](https://www.ensembl.org/info/docs/tools/vep/vep_formats.html)
- [VCF Format Specification](https://samtools.github.io/hts-specs/VCFv4.2.pdf)
- [DrugBank Database](https://www.drugbank.ca/)
- [ClinVar Database](https://www.ncbi.nlm.nih.gov/clinvar/)
- [Power BI Documentation](https://docs.microsoft.com/en-us/power-bi/)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Contributors

- Project Lead: [Your Name]
- Contributors: [List contributors]

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Contact

For questions or support, please contact: [your-email@example.com]

## 🙏 Acknowledgments

- Ensembl for providing public genomic data
- DrugBank for pharmacogenomic information
- The open-source community for tools and libraries

---

**Note**: This project is for research and educational purposes. Always consult with qualified healthcare professionals for clinical decisions.

