# Technology Stack Documentation

## Table of Contents
1. [Technology Overview](#technology-overview)
2. [Core Technologies](#core-technologies)
3. [Supporting Libraries](#supporting-libraries)
4. [Why Each Technology](#why-each-technology)
5. [Technology Comparisons](#technology-comparisons)
6. [Integration Details](#integration-details)

---

## Technology Overview

### Technology Stack Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│                                                              │
│  Power BI Desktop                                            │
│  - Business Intelligence                                     │
│  - Interactive Dashboards                                    │
│  - MySQL DirectQuery/Import                                  │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ ODBC/MySQL Connector
                              │
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│                                                              │
│  Python 3.11+                                                │
│  ├── Pandas 2.1.0+        (Data Processing)                 │
│  ├── NumPy 1.24.0+        (Numerical Computing)             │
│  ├── vcfpy 0.13.6+        (VCF Parsing)                     │
│  ├── pysam 0.21.0+        (Alternative VCF Parser)          │
│  ├── SQLAlchemy 2.0.0+    (ORM & Connection Pool)           │
│  ├── PyMySQL 1.1.0+       (MySQL Driver)                    │
│  ├── PyYAML 6.0.1+        (Configuration)                   │
│  ├── requests 2.31.0+     (HTTP Client)                     │
│  ├── tqdm 4.66.0+         (Progress Bars)                   │
│  └── pytest 7.4.0+        (Testing Framework)               │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ PyMySQL/mysql-connector
                              │
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                              │
│                                                              │
│  MySQL 8.0+                                                  │
│  - Relational Database                                       │
│  - InnoDB Storage Engine                                     │
│  - Full-Text Search                                          │
│  - Transaction Support                                       │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │ HTTPS/FTP
                              │
┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                         │
│                                                              │
│  Ensembl FTP          (Genomic Data)                        │
│  ClinVar API          (Clinical Annotations)                │
│  DrugBank API         (Drug Information)                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Technologies

### 1. Python 3.11+

**Version:** 3.11 or higher (Latest: 3.12)

**Why Python 3.11+?**

#### Performance Improvements
```
Python 3.11 vs 3.10:
- 10-60% faster execution
- Improved error messages
- Better exception handling
- Faster startup time
```

#### Modern Features Used
```python
# Type hints (PEP 484)
def process_variant(vcf_file: str, max_rows: Optional[int] = None) -> pd.DataFrame:
    pass

# Dataclasses (PEP 557)
@dataclass
class Variant:
    chromosome: str
    position: int
    reference: str

# f-strings (PEP 498)
logger.info(f"Processed {count:,} variants in {duration:.2f} seconds")

# Walrus operator (PEP 572)
if (count := len(variants)) > 0:
    process(count)
```

#### Ecosystem Advantages
- Rich bioinformatics libraries (BioPython, vcfpy, pysam)
- Excellent data science tools (pandas, numpy, scikit-learn)
- Strong database support (SQLAlchemy, PyMySQL)
- Great testing frameworks (pytest, unittest)

**Alternatives Considered:**
| Language | Pros | Cons | Why Not Chosen |
|----------|------|------|----------------|
| R | Best for statistics | Slower, harder deployment | Limited ETL capabilities |
| Java | Fast, enterprise-ready | Verbose, slower dev | Overkill for data processing |
| Scala | Spark integration | Steep learning curve | Complexity not needed |
| Go | Very fast, simple | Limited bio libraries | Immature ecosystem |

---

### 2. Pandas 2.1.0+

**Purpose:** Data manipulation and analysis

**Why Pandas?**

#### Core Strengths
```python
# Efficient data structures
df = pd.DataFrame({
    'chromosome': ['1', '2', '3'],
    'position': [1000, 2000, 3000],
    'quality': [99.5, 88.3, 95.2]
})

# Vectorized operations (fast!)
df['position'] = df['position'] * 2  # Much faster than loop

# Built-in I/O
df.to_csv('variants.csv', index=False)
df.to_sql('variants', engine, if_exists='append')

# Powerful filtering
high_quality = df[df['quality'] > 90]

# Grouping and aggregation
summary = df.groupby('chromosome').agg({
    'position': 'count',
    'quality': 'mean'
})
```

#### Memory Efficiency
```python
# Categorical data types (saves memory)
df['chromosome'] = df['chromosome'].astype('category')

# Downcast numeric types
df['position'] = pd.to_numeric(df['position'], downcast='integer')

# Chunked reading (handle large files)
for chunk in pd.read_csv('large_file.csv', chunksize=10000):
    process(chunk)
```

#### Why Version 2.1.0+?
- Copy-on-Write (CoW) for better memory management
- Improved performance for string operations
- Better PyArrow integration
- Enhanced nullable dtypes

**Alternatives:**
| Tool | Use Case | Why Not Primary |
|------|----------|-----------------|
| Dask | Distributed processing | Single-node sufficient |
| Polars | Faster than pandas | Newer, less mature |
| Spark DataFrame | Big data | Overkill for current scale |
| NumPy arrays | Numerical only | Limited functionality |

---

### 3. NumPy 1.24.0+

**Purpose:** Numerical computing foundation

**Why NumPy?**

#### Core Capabilities
```python
# Fast array operations
import numpy as np

# Vectorized calculations
positions = np.array([1000, 2000, 3000])
normalized = (positions - positions.mean()) / positions.std()

# Memory-efficient
quality_scores = np.array(scores, dtype=np.float32)  # Half size of float64

# Statistical functions
mean_quality = np.mean(quality_scores)
percentile_95 = np.percentile(quality_scores, 95)
```

#### Integration with Pandas
```python
# Pandas uses NumPy under the hood
df['position'].values  # Returns NumPy array
df['quality'].mean()   # Uses NumPy functions
```

**Why Version 1.24.0+?**
- Better memory layout for multi-dimensional arrays
- Improved type promotion rules
- Faster string operations
- Better Python 3.11+ compatibility

---

### 4. MySQL 8.0+

**Purpose:** Relational database for genomic data

**Why MySQL 8.0+?**

#### Key Features Used

##### 1. Window Functions
```sql
-- Rank variants by quality within each chromosome
SELECT 
    chromosome,
    position,
    quality,
    RANK() OVER (PARTITION BY chromosome ORDER BY quality DESC) as rank
FROM variants;
```

##### 2. Common Table Expressions (CTEs)
```sql
-- Complex query with CTEs
WITH high_quality AS (
    SELECT * FROM variants WHERE quality > 90
),
annotated AS (
    SELECT v.*, g.gene_name 
    FROM high_quality v
    JOIN genes g ON v.gene_symbol = g.gene_symbol
)
SELECT * FROM annotated;
```

##### 3. JSON Support
```sql
-- Store and query JSON data
ALTER TABLE variants ADD COLUMN metadata JSON;

SELECT * FROM variants 
WHERE JSON_EXTRACT(metadata, '$.type') = 'SNP';
```

##### 4. Full-Text Search
```sql
-- Fast text search on gene names
CREATE FULLTEXT INDEX idx_gene_name ON genes(gene_name);

SELECT * FROM genes 
WHERE MATCH(gene_name) AGAINST('BRCA1' IN NATURAL LANGUAGE MODE);
```

##### 5. Improved Performance
```
MySQL 8.0 vs 5.7:
- 2x faster for read queries
- Better query optimizer
- Faster JSON operations
- Improved index performance
```

#### Configuration for Genomic Data
```ini
[mysqld]
# Buffer pool (hold data in memory)
innodb_buffer_pool_size = 8G

# Log file size (for large transactions)
innodb_log_file_size = 512M

# Connections
max_connections = 200

# Query cache (deprecated but useful)
query_cache_size = 64M

# Character set (for international gene names)
character_set_server = utf8mb4
collation_server = utf8mb4_unicode_ci
```

**Alternatives:**
| Database | Pros | Cons | Why Not Chosen |
|----------|------|------|----------------|
| PostgreSQL | More features | Less Power BI integration | Similar but different |
| MongoDB | Flexible schema | No JOINs, no ACID | Not suitable for relational data |
| Cassandra | Massive scale | Complex, overkill | Current scale doesn't need it |
| SQLite | Simple, embedded | Single user only | Not for production |
| Oracle | Enterprise features | Expensive | Cost prohibitive |

---

### 5. SQLAlchemy 2.0.0+

**Purpose:** Python SQL toolkit and ORM

**Why SQLAlchemy?**

#### Core Advantages

##### 1. Connection Pooling
```python
# Automatic connection management
engine = create_engine(
    'mysql+pymysql://user:pass@localhost/db',
    pool_size=10,          # Keep 10 connections ready
    max_overflow=20,       # Allow 20 more if needed
    pool_recycle=3600,     # Recycle connections hourly
    pool_pre_ping=True     # Test connections before use
)
```

##### 2. Database Agnostic
```python
# Same code works with different databases
# Just change connection string:
# 'mysql+pymysql://...'    # MySQL
# 'postgresql://...'       # PostgreSQL
# 'sqlite:///...'          # SQLite
```

##### 3. Transaction Management
```python
# Automatic transaction handling
with engine.begin() as connection:
    connection.execute(text("INSERT INTO variants ..."))
    connection.execute(text("INSERT INTO genes ..."))
    # Auto-commit if no errors, auto-rollback if error
```

##### 4. SQL Injection Prevention
```python
# Parameterized queries (safe)
query = text("SELECT * FROM variants WHERE gene = :gene")
result = connection.execute(query, {"gene": gene_name})
```

##### 5. ORM Capabilities (Optional)
```python
# Object-Relational Mapping
from sqlalchemy.orm import declarative_base, Session

Base = declarative_base()

class Variant(Base):
    __tablename__ = 'variants'
    id = Column(String(36), primary_key=True)
    chromosome = Column(String(10))
    position = Column(Integer)
    
# Query like objects
session = Session(engine)
variants = session.query(Variant).filter(Variant.chromosome == '1').all()
```

**Why Version 2.0.0+?**
- Modern async support
- Better type hints
- Improved performance
- Cleaner API

---

### 6. vcfpy 0.13.6+ & pysam 0.21.0+

**Purpose:** VCF file parsing

**Why Two Libraries?**

#### vcfpy
```python
# Pure Python, easier to understand
import vcfpy

reader = vcfpy.Reader.from_path('variants.vcf')
for record in reader:
    print(record.CHROM, record.POS, record.REF, record.ALT)
    print(record.INFO)  # Dictionary of INFO fields
```

**Pros:**
- Pure Python (no compilation)
- Easy to debug
- Readable code
- Good documentation

**Cons:**
- Slower than pysam
- Higher memory usage

#### pysam
```python
# C-based, much faster
import pysam

vcf = pysam.VariantFile('variants.vcf')
for record in vcf:
    print(record.chrom, record.pos, record.ref, record.alts)
```

**Pros:**
- Very fast (C-based)
- Lower memory usage
- Industry standard

**Cons:**
- Requires compilation
- Harder to debug
- Platform dependent

**Our Strategy:**
```python
# Default: Use vcfpy (easier)
# Option: Use pysam (faster) with --use-vcfpy flag
if use_vcfpy:
    parser = VCFPyParser()
else:
    parser = PysamParser()
```

---

### 7. PyYAML 6.0.1+

**Purpose:** Configuration file parsing

**Why YAML?**

#### Advantages Over Alternatives

```yaml
# YAML - Human readable
database:
  host: localhost
  port: 3306
  user: root
  pool_size: 10
```

vs.

```json
// JSON - No comments, less readable
{
  "database": {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "pool_size": 10
  }
}
```

vs.

```ini
# INI - Limited structure
[database]
host = localhost
port = 3306
user = root
pool_size = 10
```

#### YAML Features Used
```yaml
# Comments
# This is a comment

# Lists
chromosomes:
  - chr1
  - chr2
  - chrX

# Nested structures
processing:
  vcf_parser:
    extract_info_fields:
      - AF
      - AC
      - AN

# References (DRY)
default_settings: &defaults
  timeout: 30
  retries: 3

api_config:
  <<: *defaults
  endpoint: "https://api.example.com"
```

**Why Version 6.0.1+?**
- Security fixes (arbitrary code execution)
- Better error messages
- Improved performance
- Full Python 3.11 support

---

### 8. requests 2.31.0+

**Purpose:** HTTP client for API calls

**Why requests?**

#### Simple, Elegant API
```python
import requests

# Simple GET request
response = requests.get('https://api.example.com/data')
data = response.json()

# POST with data
response = requests.post(
    'https://api.example.com/submit',
    json={'gene': 'BRCA1'},
    headers={'Authorization': 'Bearer TOKEN'}
)

# Error handling
try:
    response.raise_for_status()
except requests.exceptions.HTTPError as e:
    logger.error(f"API error: {e}")

# Timeout handling
response = requests.get(url, timeout=30)

# Session for connection pooling
session = requests.Session()
session.headers.update({'User-Agent': 'GenomicPipeline/1.0'})
```

#### Features Used
- Connection pooling (reuse TCP connections)
- Automatic decompression (gzip, deflate)
- JSON decoding built-in
- SSL certificate verification
- Timeout handling
- Retry logic (with urllib3)

**Alternatives:**
| Library | Pros | Cons |
|---------|------|------|
| urllib (stdlib) | No dependency | Verbose, low-level |
| httpx | Async support | Newer, less mature |
| aiohttp | Fast async | Complexity not needed |

---

### 9. tqdm 4.66.0+

**Purpose:** Progress bars

**Why tqdm?**

#### User Experience Enhancement
```python
from tqdm import tqdm

# Simple progress bar
for item in tqdm(items, desc="Processing"):
    process(item)

# Custom format
for chunk in tqdm(chunks, total=total_chunks, 
                  desc="Loading", unit="chunk"):
    load(chunk)

# Nested progress bars
for chromosome in tqdm(chromosomes, desc="Chromosomes"):
    for variant in tqdm(variants, desc=f"  {chromosome}", leave=False):
        process(variant)

# With file downloads
with tqdm(total=file_size, unit='B', unit_scale=True) as pbar:
    for chunk in response.iter_content(chunk_size=8192):
        file.write(chunk)
        pbar.update(len(chunk))
```

**Output:**
```
Processing variants: 45%|████████      | 450000/1000000 [02:15<02:45, 3333.33it/s]
```

#### Benefits
- Users know progress (not frozen)
- Estimate time remaining
- Identify slow operations
- Professional appearance

---

### 10. Power BI Desktop

**Purpose:** Data visualization and dashboards

**Why Power BI?**

#### Key Advantages

##### 1. DirectQuery to MySQL
```
Real-time connection to database:
- Always shows latest data
- No data refresh needed
- Security controlled by database
```

##### 2. Rich Visualizations
- 30+ built-in chart types
- Custom visuals from marketplace
- Interactive filtering
- Drill-down capabilities

##### 3. DAX Language
```dax
// Calculate variant frequency
VariantFrequency = 
    DIVIDE(
        COUNTROWS(variants),
        CALCULATE(COUNTROWS(variants), ALL(variants[chromosome]))
    )

// Year-over-year comparison
YoY_Growth = 
    VAR CurrentYear = SUM(variants[count])
    VAR PreviousYear = CALCULATE(SUM(variants[count]), SAMEPERIODLASTYEAR(dates[Date]))
    RETURN DIVIDE(CurrentYear - PreviousYear, PreviousYear)
```

##### 4. Business Intelligence Features
- Automatic insights
- Q&A natural language queries
- Mobile app support
- Sharing and collaboration

**Alternatives:**
| Tool | Pros | Cons | Why Not Primary |
|------|------|------|-----------------|
| Tableau | More powerful | Expensive | Cost |
| Grafana | Open source | Less BI features | More for metrics |
| Metabase | Simple, open | Limited visuals | Less powerful |
| Jupyter | Programmable | Not for end-users | Technical only |

---

## Supporting Libraries

### Testing: pytest 7.4.0+

**Why pytest?**

```python
# Simple syntax
def test_vcf_parser():
    result = parse_vcf('test.vcf')
    assert len(result) == 100
    assert result[0]['chromosome'] == '1'

# Fixtures for setup
@pytest.fixture
def sample_data():
    return pd.DataFrame({'col': [1, 2, 3]})

def test_transform(sample_data):
    result = transform(sample_data)
    assert len(result) == 3

# Parameterized tests
@pytest.mark.parametrize("input,expected", [
    ("1", "chr1"),
    ("X", "chrX"),
])
def test_chromosome_conversion(input, expected):
    assert convert_chromosome(input) == expected

# Coverage reporting
# pytest --cov=src --cov-report=html
```

**Features:**
- Simple assert statements
- Powerful fixtures
- Parametrized tests
- Plugin ecosystem
- Coverage integration

---

### Logging: Python logging (stdlib)

**Why Standard Logging?**

```python
import logging

# Hierarchical loggers
logger = logging.getLogger('genomic.etl.extract')

# Multiple handlers
console_handler = logging.StreamHandler()
file_handler = logging.RotatingFileHandler('app.log', maxBytes=10MB)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Levels for filtering
logger.debug("Parsing line 12345")      # Development only
logger.info("Processing chromosome 1")   # Normal operation
logger.warning("Missing annotation")     # Potential issue
logger.error("Database connection failed") # Error occurred
logger.critical("Out of memory")         # System failure

# Structured logging
logger.info("Processed variants", extra={
    'chromosome': '1',
    'count': 1000,
    'duration': 45.2
})
```

---

## Technology Comparisons

### Data Processing: Pandas vs Alternatives

| Feature | Pandas | Polars | Dask | Spark |
|---------|--------|--------|------|-------|
| Speed | ★★★☆☆ | ★★★★★ | ★★★☆☆ | ★★★★☆ |
| Memory | ★★★☆☆ | ★★★★☆ | ★★★★☆ | ★★★★★ |
| Ease of Use | ★★★★★ | ★★★★☆ | ★★★☆☆ | ★★☆☆☆ |
| Maturity | ★★★★★ | ★★★☆☆ | ★★★★☆ | ★★★★★ |
| Ecosystem | ★★★★★ | ★★☆☆☆ | ★★★★☆ | ★★★★★ |
| **Best For** | Single-node | Speed critical | Distributed | Big data |
| **Our Use** | ✅ Primary | Future option | If needed | Overkill |

### Database: MySQL vs Alternatives

| Feature | MySQL | PostgreSQL | MongoDB | Cassandra |
|---------|-------|------------|---------|-----------|
| SQL Support | ★★★★★ | ★★★★★ | ★☆☆☆☆ | ★★☆☆☆ |
| Performance | ★★★★☆ | ★★★★☆ | ★★★★☆ | ★★★★★ |
| ACID | ★★★★★ | ★★★★★ | ★★★☆☆ | ★★☆☆☆ |
| Scalability | ★★★☆☆ | ★★★☆☆ | ★★★★★ | ★★★★★ |
| Power BI | ★★★★★ | ★★★★☆ | ★★★☆☆ | ★★☆☆☆ |
| **Best For** | OLTP/OLAP | Advanced SQL | Documents | Massive scale |
| **Our Use** | ✅ Primary | Alternative | Not suitable | Overkill |

---

## Integration Details

### Python ↔ MySQL Integration

```python
# Method 1: SQLAlchemy (ORM)
from sqlalchemy import create_engine
engine = create_engine('mysql+pymysql://user:pass@localhost/db')
df.to_sql('variants', engine, if_exists='append', index=False)

# Method 2: PyMySQL (Direct)
import pymysql
conn = pymysql.connect(host='localhost', user='root', password='pass')
cursor = conn.cursor()
cursor.execute("INSERT INTO variants VALUES (%s, %s)", (chr, pos))

# Method 3: mysql-connector-python (Official)
import mysql.connector
conn = mysql.connector.connect(host='localhost', user='root')
```

**Our Choice: SQLAlchemy + PyMySQL**
- Best performance
- Connection pooling
- Database agnostic
- Transaction support

### Power BI ↔ MySQL Integration

```
Method 1: DirectQuery (Real-time)
Power BI → MySQL ODBC Driver → MySQL Server
- Always current data
- No refresh needed
- Query pushed to database

Method 2: Import Mode (Faster)
Power BI → Import data → In-memory cache
- Faster visualizations
- Needs refresh schedule
- More features available
```

**Our Recommendation: DirectQuery for real-time, Import for performance**

---

## Version Management

### Dependency Pinning Strategy

```txt
# requirements.txt

# Exact version (critical dependencies)
pandas==2.1.0

# Minimum version (minor updates OK)
numpy>=1.24.0

# Compatible release (patch updates OK)
sqlalchemy~=2.0.0  # Allows 2.0.x, not 2.1.0

# Range (for testing)
pytest>=7.4.0,<8.0.0
```

### Upgrading Strategy

```bash
# Check for updates
pip list --outdated

# Update specific package
pip install --upgrade pandas

# Update all (carefully!)
pip install --upgrade -r requirements.txt

# Test after upgrade
pytest tests/
```

---

## Performance Optimization

### Pandas Optimization
```python
# Use categorical for repeated strings
df['chromosome'] = df['chromosome'].astype('category')

# Use appropriate dtypes
df['position'] = df['position'].astype('int32')  # Not int64

# Avoid iterrows (slow)
for idx, row in df.iterrows():  # BAD
    process(row)

# Use vectorization (fast)
df['new_col'] = df['old_col'] * 2  # GOOD
```

### MySQL Optimization
```sql
-- Add indexes
CREATE INDEX idx_gene ON variants(gene_symbol);
CREATE INDEX idx_chrom_pos ON variants(chromosome, position);

-- Use EXPLAIN to analyze queries
EXPLAIN SELECT * FROM variants WHERE gene_symbol = 'BRCA1';

-- Optimize table
OPTIMIZE TABLE variants;
```

---

## Conclusion

This technology stack provides:
- ✅ **Performance:** Fast processing of millions of variants
- ✅ **Reliability:** Proven, mature technologies
- ✅ **Maintainability:** Clear, readable code
- ✅ **Scalability:** Can grow with data size
- ✅ **Cost:** All open-source (except Power BI)

Each technology was chosen for specific reasons, with alternatives considered and documented.

