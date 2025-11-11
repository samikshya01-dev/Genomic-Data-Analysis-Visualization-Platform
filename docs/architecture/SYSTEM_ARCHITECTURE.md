# System Architecture Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architectural Patterns](#architectural-patterns)
3. [System Components](#system-components)
4. [Data Flow](#data-flow)
5. [Design Decisions](#design-decisions)
6. [Scalability Considerations](#scalability-considerations)

---

## Overview

### High-Level Architecture

The Genomic Data Analysis Platform follows a **Layered Architecture** pattern with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                       │
│                    (Power BI Dashboard)                      │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                        │
│              (ETL Pipeline + Analysis Engine)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Extraction  │  │Transformation│  │   Loading    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │  Enrichment  │  │   Analysis   │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│    ┌──────────────┐        ┌──────────────┐                │
│    │    MySQL     │        │  File System │                │
│    │   Database   │        │   (CSV/VCF)  │                │
│    └──────────────┘        └──────────────┘                │
└─────────────────────────────────────────────────────────────┘
                              ▲
                              │
┌─────────────────────────────────────────────────────────────┐
│                    External Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Ensembl    │  │   ClinVar    │  │  DrugBank    │      │
│  │     FTP      │  │     API      │  │     API      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## Architectural Patterns

### 1. **Layered Architecture**

**Why chosen:**
- Clear separation of concerns
- Easy to maintain and test
- Independent layer development
- Flexible for future changes

**Implementation:**
```
Layer 1: Presentation (Power BI)
Layer 2: Application Logic (ETL + Analysis)
Layer 3: Data Access (MySQL + File I/O)
Layer 4: External Services (APIs + FTP)
```

### 2. **Pipeline Pattern (ETL)**

**Why chosen:**
- Sequential data processing
- Clear transformation stages
- Easy to debug and monitor
- Supports partial execution

**Stages:**
```
Extract → Transform → Enrich → Load → Analyze
```

### 3. **Repository Pattern**

**Why chosen:**
- Abstracts data access logic
- Easy to switch databases
- Testable with mocks
- Centralized data operations

**Implementation:**
```python
DatabaseConfig (Repository)
├── Connection management
├── Transaction handling
└── Query execution
```

### 4. **Factory Pattern**

**Why chosen:**
- Flexible object creation
- Encapsulates initialization logic
- Easy to extend

**Usage:**
```python
# Logger Factory
get_logger(name) → Logger instance

# Database Factory
get_db_config(path) → DatabaseConfig instance
```

### 5. **Singleton Pattern**

**Why chosen:**
- Single shared instance (logger, db config)
- Resource conservation
- Consistent state

**Implementation:**
```python
_logger_manager = None  # Global singleton
_db_config = None       # Global singleton
```

---

## System Components

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        src/main.py                           │
│                  (GenomicPipeline Class)                     │
│                  - Orchestrates workflow                     │
│                  - Manages execution flow                    │
└─────────────────────────────────────────────────────────────┘
         │
         ├───────────────────────────────────────┐
         ▼                                       ▼
┌──────────────────────┐            ┌──────────────────────┐
│    ETL Modules       │            │  Analysis Modules    │
│  ┌────────────────┐  │            │  ┌────────────────┐  │
│  │ VCFExtractor   │  │            │  │ VariantSummary │  │
│  │ VCFTransformer │  │            │  │ MutationAnalysis│ │
│  │ MySQLLoader    │  │            │  └────────────────┘  │
│  │ AnnotationEnr. │  │            └──────────────────────┘
│  └────────────────┘  │
└──────────────────────┘
         │
         ▼
┌──────────────────────┐
│   Utility Modules    │
│  ┌────────────────┐  │
│  │ Logger         │  │
│  │ DatabaseConfig │  │
│  │ FileUtils      │  │
│  └────────────────┘  │
└──────────────────────┘
```

### 1. **Main Pipeline (Orchestrator)**

**Responsibility:** Coordinate all pipeline phases

**Key Methods:**
- `run_extraction()` - Download and extract VCF
- `run_transformation()` - Parse and normalize data
- `run_enrichment()` - Add clinical annotations
- `run_loading()` - Insert into database
- `run_analysis()` - Generate reports
- `run_full_pipeline()` - Execute complete workflow

**Why this design:**
- Single entry point for all operations
- Centralized error handling
- Easy to add new phases
- Clear execution flow

### 2. **ETL Modules**

#### **VCFExtractor**
```python
Responsibility: Download and extract VCF files
├── download_vcf() - HTTP download with progress
├── extract_vcf() - Gzip decompression
└── extract_all() - Complete extraction workflow
```

**Why separate:**
- Reusable for different data sources
- Easy to test independently
- Can be replaced with alternative sources

#### **VCFTransformer**
```python
Responsibility: Parse VCF and normalize data
├── parse_vcf() - Read VCF format
├── extract_variants() - Extract variant records
├── extract_genes() - Extract gene information
└── transform_all() - Complete transformation
```

**Why separate:**
- Complex parsing logic isolated
- Can support multiple VCF versions
- Memory optimization per phase

#### **MySQLLoader**
```python
Responsibility: Load data into MySQL
├── create_tables() - DDL operations
├── insert_variants() - Batch inserts
├── insert_genes() - Gene data loading
└── load_all() - Complete loading workflow
```

**Why separate:**
- Database operations isolated
- Easy to switch to different DB
- Transaction management centralized

#### **AnnotationEnricher**
```python
Responsibility: Add clinical annotations
├── fetch_clinvar_data() - ClinVar API calls
├── fetch_drugbank_data() - DrugBank queries
└── enrich_all() - Complete enrichment
```

**Why separate:**
- External API calls isolated
- Easy to add new data sources
- Caching can be implemented here

### 3. **Analysis Modules**

#### **VariantSummary**
```python
Responsibility: Generate summary statistics
├── count_variants() - Total counts
├── count_by_chromosome() - Per-chromosome stats
├── count_by_gene() - Gene-level stats
└── generate_all_summaries() - All summaries
```

#### **MutationAnalysis**
```python
Responsibility: Detailed mutation analysis
├── calculate_frequencies() - Allele frequencies
├── analyze_clinical_significance() - Clinical stats
└── generate_mutation_report() - Complete report
```

### 4. **Utility Modules**

#### **Logger**
```python
Responsibility: Centralized logging
├── Console logging
├── File rotation
├── Level management
└── Execution time tracking
```

**Why centralized:**
- Consistent log format
- Easy to change log configuration
- Centralized log aggregation

#### **DatabaseConfig**
```python
Responsibility: Database connection management
├── Connection pooling
├── Transaction handling
├── Configuration loading
└── Connection testing
```

**Why separate:**
- Database logic centralized
- Easy to implement connection pooling
- Configuration management

#### **FileUtils**
```python
Responsibility: File operations
├── Download with progress
├── Compression/decompression
├── File size utilities
└── Configuration loading
```

---

## Data Flow

### Complete Pipeline Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: EXTRACTION                                          │
├─────────────────────────────────────────────────────────────┤
│ Input:  Ensembl FTP URL                                      │
│ Action: Download VCF.gz → Extract to VCF                     │
│ Output: data/raw/homo_sapiens-chrX.vcf                      │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: TRANSFORMATION                                      │
├─────────────────────────────────────────────────────────────┤
│ Input:  VCF file                                             │
│ Action: Parse VCF → Extract fields → Normalize types        │
│ Output: variants_df (DataFrame), genes_df (DataFrame)       │
│         data/processed/variants.csv                          │
│         data/processed/genes.csv                             │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 3: ENRICHMENT (Optional)                               │
├─────────────────────────────────────────────────────────────┤
│ Input:  genes_df                                             │
│ Action: Query ClinVar API → Query DrugBank API              │
│ Output: enriched_genes_df, drug_annotations_df              │
│         data/processed/drug_annotations.csv                  │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 4: LOADING                                             │
├─────────────────────────────────────────────────────────────┤
│ Input:  DataFrames (variants, genes, annotations)           │
│ Action: Create tables → Batch insert → Create indexes       │
│ Output: MySQL database populated                            │
│         - variants table                                     │
│         - genes table                                        │
│         - drug_annotations table                             │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ PHASE 5: ANALYSIS                                            │
├─────────────────────────────────────────────────────────────┤
│ Input:  MySQL database                                       │
│ Action: Run SQL queries → Calculate statistics              │
│ Output: Reports, summary tables                             │
│         data/processed/mutation_report_*.txt                 │
│         mutation_summary table                               │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ PRESENTATION: Power BI                                       │
├─────────────────────────────────────────────────────────────┤
│ Input:  MySQL database                                       │
│ Action: Connect → Query → Visualize                         │
│ Output: Interactive dashboards                               │
└─────────────────────────────────────────────────────────────┘
```

### Data Transformation Details

```
VCF Format                   Normalized DataFrame
-----------                  --------------------
#CHROM POS ID REF ALT   →   variant_id: UUID
                             chromosome: String (1-22, X, Y)
                             position: Integer
                             reference: String
                             alternate: String
                             quality: Float
                             gene_symbol: String
                             clinical_significance: String
                             allele_frequency: Float
                             ... (15 total columns)
```

---

## Design Decisions

### 1. **Why Python?**

**Decision:** Use Python 3.11+ as primary language

**Rationale:**
- Rich ecosystem for bioinformatics (pandas, numpy, vcfpy)
- Easy to learn and maintain
- Excellent data processing capabilities
- Strong community support
- Integration with MySQL and Power BI

**Alternatives considered:**
- R: Better for statistics but harder deployment
- Java: More verbose, slower development
- Scala/Spark: Overkill for single-node processing

### 2. **Why MySQL?**

**Decision:** Use MySQL 8.0+ as primary database

**Rationale:**
- Mature, stable RDBMS
- Excellent performance for analytical queries
- Wide tool support (Power BI, MySQL Workbench)
- ACID compliance for data integrity
- Good indexing capabilities

**Alternatives considered:**
- PostgreSQL: Similar but less Power BI integration
- MongoDB: Not suitable for relational genomic data
- SQLite: Not suitable for multi-user access
- Cassandra/HBase: Overkill for current scale

### 3. **Why Pandas DataFrames?**

**Decision:** Use pandas as intermediate data structure

**Rationale:**
- Memory-efficient for millions of rows
- Rich transformation API
- Easy integration with MySQL (SQLAlchemy)
- Vectorized operations (fast)
- CSV export/import built-in

**Alternatives considered:**
- Pure Python lists: Too slow for large data
- NumPy arrays: Less flexible for mixed types
- Dask DataFrames: Unnecessary for single-node

### 4. **Why Batch Processing?**

**Decision:** Process data in configurable chunks

**Rationale:**
- Memory efficiency (process 50K rows at a time)
- Progress tracking
- Ability to resume on failure
- Handles files of any size

**Implementation:**
```yaml
processing:
  chunk_size: 50000      # Configurable
  max_workers: 4         # Parallel processing
```

### 5. **Why YAML Configuration?**

**Decision:** Use YAML for configuration files

**Rationale:**
- Human-readable and editable
- Supports complex structures
- Industry standard
- Easy validation

**Alternatives considered:**
- JSON: Less readable, no comments
- INI: Limited structure support
- Environment variables: Not suitable for complex config

### 6. **Why Connection Pooling?**

**Decision:** Implement connection pooling with SQLAlchemy

**Rationale:**
- Reuse database connections (performance)
- Handle concurrent access
- Automatic connection management
- Industry best practice

**Configuration:**
```yaml
pool_size: 10
max_overflow: 20
pool_timeout: 30
pool_recycle: 3600
```

### 7. **Why Modular Design?**

**Decision:** Separate concerns into modules

**Rationale:**
- Single Responsibility Principle
- Easy to test individually
- Can be reused in other projects
- Parallel development
- Easy to maintain

**Structure:**
```
src/
├── etl/          # ETL operations
├── analysis/     # Analysis operations
└── utils/        # Shared utilities
```

---

## Scalability Considerations

### Current Scale

- **Data Volume:** ~1-5M variants per chromosome
- **Processing Time:** 30-60 minutes per chromosome
- **Memory Usage:** 4-8 GB RAM
- **Disk Space:** 10-50 GB per chromosome

### Horizontal Scaling Options

#### 1. **Multi-Chromosome Parallel Processing**

```python
# Process multiple chromosomes in parallel
chromosomes = ['chr1', 'chr2', ..., 'chrX']
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(process_chromosome, chr) 
               for chr in chromosomes]
```

#### 2. **Distributed Processing (Future)**

```
Apache Spark for large-scale processing:
- Distribute VCF parsing across cluster
- Parallel transformations
- Distributed writes to database
```

#### 3. **Database Partitioning**

```sql
-- Partition variants table by chromosome
CREATE TABLE variants (
    variant_id VARCHAR(36),
    chromosome VARCHAR(10),
    ...
) PARTITION BY LIST (chromosome) (
    PARTITION p1 VALUES IN ('1'),
    PARTITION p2 VALUES IN ('2'),
    ...
);
```

### Vertical Scaling Options

#### 1. **Memory Optimization**

```python
# Use categorical data types
df['chromosome'] = df['chromosome'].astype('category')

# Use smaller numeric types
df['position'] = df['position'].astype('int32')
df['quality'] = df['quality'].astype('float32')
```

#### 2. **Database Optimization**

```sql
-- Optimize MySQL configuration
innodb_buffer_pool_size = 8G
innodb_log_file_size = 512M
max_connections = 200
```

### Performance Bottlenecks

1. **VCF Parsing:** I/O bound
   - Solution: Use faster parsers (pysam), parallel processing

2. **Database Inserts:** Network bound
   - Solution: Batch inserts, larger batch sizes

3. **Enrichment APIs:** Rate limited
   - Solution: Caching, batch API calls

4. **Memory:** Large chromosomes
   - Solution: Chunk processing, streaming

---

## Security Architecture

### 1. **Configuration Security**

```
Sensitive data isolated:
- Database credentials in config files
- API keys in environment variables
- .gitignore prevents credential commits
```

### 2. **Database Access**

```python
# Parameterized queries (SQL injection prevention)
cursor.execute("SELECT * FROM variants WHERE gene = %s", (gene,))

# Connection encryption (optional)
ssl_config = {
    'ca': '/path/to/ca-cert.pem',
    'cert': '/path/to/client-cert.pem',
    'key': '/path/to/client-key.pem'
}
```

### 3. **Input Validation**

```python
# Validate VCF format before processing
# Validate data types during transformation
# Check for malicious file paths
```

---

## Monitoring & Observability

### 1. **Logging Strategy**

```
Levels:
- ERROR: Pipeline failures, database errors
- WARNING: Missing data, API timeouts
- INFO: Phase completion, progress updates
- DEBUG: Detailed execution flow

Outputs:
- Console: Real-time monitoring
- Files: Persistent logs with rotation
```

### 2. **Metrics to Track**

```
Performance Metrics:
- Rows processed per second
- Database insert rate
- Memory usage
- API response times

Business Metrics:
- Total variants processed
- Genes annotated
- Quality score distribution
```

### 3. **Error Handling**

```python
# Graceful degradation
try:
    enriched_data = enrich_from_api()
except APIException:
    logger.warning("API unavailable, skipping enrichment")
    enriched_data = original_data
```

---

## Testing Strategy

### 1. **Unit Tests**

```python
# Test individual components
test_vcf_parser.py      # VCF parsing logic
test_db_inserts.py      # Database operations
test_data_quality.py    # Data validation
```

### 2. **Integration Tests**

```python
# Test component interactions
test_etl_pipeline.py    # Full ETL flow
test_database_integration.py  # DB connections
```

### 3. **End-to-End Tests**

```bash
# Test complete pipeline with sample data
make test-run  # Process 10K rows
```

---

## Future Architecture Evolution

### Phase 2 Enhancements

1. **REST API Layer**
   ```
   FastAPI/Flask API for programmatic access
   - GET /variants/{gene}
   - GET /statistics/summary
   - POST /analyze
   ```

2. **Caching Layer**
   ```
   Redis for API response caching
   - Cache enrichment results
   - Cache frequently accessed queries
   ```

3. **Message Queue**
   ```
   RabbitMQ/Kafka for async processing
   - Queue chromosome processing jobs
   - Event-driven architecture
   ```

### Phase 3: Cloud Migration

```
AWS Architecture:
├── S3: Store VCF files
├── Lambda: Serverless processing
├── RDS: Managed MySQL
├── EC2: Processing nodes
└── CloudWatch: Monitoring
```

---

## Conclusion

This architecture provides:
- ✅ Clear separation of concerns
- ✅ Scalability for growing data
- ✅ Maintainability for long-term evolution
- ✅ Performance for real-time analysis
- ✅ Flexibility for future enhancements

The design balances **simplicity** (easy to understand and maintain) with **sophistication** (production-ready patterns and practices).

