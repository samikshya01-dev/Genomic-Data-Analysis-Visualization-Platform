# Technical Interview Q&A - Deep Dive

## Advanced Technical Questions with Detailed Answers

---

## Database & SQL Questions

### Q1: Explain the difference between DirectQuery and Import mode in Power BI. Which did you choose and why?

**Answer:**

**DirectQuery Mode:**
```
Power BI ──→ Query ──→ MySQL ──→ Return Results ──→ Display
           (Real-time)
```
- Queries executed on MySQL in real-time
- Always shows latest data
- Limited to certain visuals
- Slower performance
- Data stays in database (security)

**Import Mode:**
```
Power BI ──→ Load Data ──→ In-Memory Cache ──→ Query Cache ──→ Display
           (One-time)
```
- Data loaded into Power BI memory
- Fast performance (in-memory)
- All visuals available
- Requires refresh schedule
- Data size limitations

**My Choice: DirectQuery**

**Reasoning:**
1. **Real-time data:** ETL runs daily, users need latest data
2. **Large dataset:** Millions of variants don't fit in Power BI memory limit (10GB)
3. **Security:** Data stays in MySQL, controlled by database permissions
4. **Cost:** Don't need Power BI Premium for large datasets

**Tradeoff:**
- Slower query performance
- Solution: Pre-aggregated `mutation_summary` table for common queries

**Hybrid Approach (Future):**
```sql
-- Keep large detailed data in DirectQuery
Variants table: DirectQuery

-- Import pre-aggregated data for fast dashboards
Mutation_summary table: Import mode
```

---

### Q2: How would you optimize this SQL query?

**Given Query:**
```sql
SELECT v.gene_symbol, COUNT(*) as variant_count, AVG(v.quality) as avg_quality
FROM variants v
WHERE v.chromosome = '1' AND v.quality > 90
GROUP BY v.gene_symbol
HAVING COUNT(*) > 100
ORDER BY variant_count DESC;
```

**Answer:**

**Analysis:**
```sql
EXPLAIN SELECT ...
-- Shows: Full table scan, no index use
```

**Optimizations:**

**1. Add Composite Index:**
```sql
CREATE INDEX idx_chrom_quality_gene 
ON variants(chromosome, quality, gene_symbol);
```
**Why:** MySQL can use index for WHERE, GROUP BY, and ORDER BY

**2. Filter Before Aggregation:**
```sql
-- Original processes all rows, then filters
-- Better: Pre-filter with CTE
WITH filtered_variants AS (
    SELECT gene_symbol, quality
    FROM variants
    WHERE chromosome = '1' AND quality > 90
)
SELECT 
    gene_symbol,
    COUNT(*) as variant_count,
    AVG(quality) as avg_quality
FROM filtered_variants
GROUP BY gene_symbol
HAVING variant_count > 100
ORDER BY variant_count DESC;
```

**3. Use Indexed Columns in SELECT:**
```sql
-- If you only need count, not average
SELECT gene_symbol, COUNT(*) as variant_count
FROM variants
WHERE chromosome = '1' AND quality > 90
GROUP BY gene_symbol
HAVING COUNT(*) > 100
ORDER BY variant_count DESC;
```
**Why:** Fewer columns = faster processing

**4. Consider Materialized View:**
```sql
-- For frequently run query, pre-compute results
CREATE TABLE variant_summary AS
SELECT 
    chromosome,
    gene_symbol,
    COUNT(*) as variant_count,
    AVG(quality) as avg_quality
FROM variants
GROUP BY chromosome, gene_symbol;

-- Then query is simple
SELECT * FROM variant_summary
WHERE chromosome = '1' AND avg_quality > 90 AND variant_count > 100;
```

**Performance Comparison:**
| Optimization | Time | Improvement |
|--------------|------|-------------|
| Original | 45s | Baseline |
| + Index | 8s | 5.6x faster |
| + CTE | 6s | 7.5x faster |
| + Materialized | 0.1s | 450x faster |

**My Implementation:**
- Added indexes for common query patterns
- Created `mutation_summary` table (materialized view)
- Updated summary table after each ETL run

---

### Q3: Explain ACID properties and how you ensure them in your pipeline.

**Answer:**

**ACID:**
- **Atomicity:** All or nothing
- **Consistency:** Valid state always
- **Isolation:** Transactions don't interfere
- **Durability:** Committed data persists

**My Implementation:**

**1. Atomicity (All or Nothing)**
```python
with engine.begin() as connection:
    try:
        # Either all succeed or all rollback
        connection.execute("INSERT INTO variants ...")
        connection.execute("INSERT INTO genes ...")
        connection.execute("INSERT INTO drug_annotations ...")
        # Auto-commit if all succeed
    except Exception as e:
        # Auto-rollback if any fails
        logger.error(f"Transaction failed: {e}")
        raise
```

**Example:**
```
Scenario: Loading 1M variants and 1K genes
If 999,999 variants succeed but 1 gene fails:
→ All 1M variants are rolled back
→ Database stays in consistent state
```

**2. Consistency (Valid State)**
```sql
-- Constraints ensure valid data
CREATE TABLE variants (
    variant_id VARCHAR(36) PRIMARY KEY,
    position INT NOT NULL CHECK (position > 0),
    quality DECIMAL(5,2) CHECK (quality >= 0 AND quality <= 100),
    gene_id VARCHAR(36),
    FOREIGN KEY (gene_id) REFERENCES genes(gene_id),
    UNIQUE KEY (chromosome, position, reference, alternate)
);
```

**Example:**
```
Try to insert: position = -100
→ Rejected by CHECK constraint
Try to insert: duplicate variant
→ Rejected by UNIQUE constraint
Try to insert: gene_id not in genes table
→ Rejected by FOREIGN KEY constraint
```

**3. Isolation (No Interference)**
```python
# Use appropriate isolation level
engine = create_engine(
    connection_string,
    isolation_level="READ_COMMITTED"  # Default MySQL level
)
```

**Isolation Levels:**
| Level | Dirty Read | Non-Repeatable | Phantom |
|-------|------------|----------------|---------|
| READ UNCOMMITTED | ✗ Possible | ✗ Possible | ✗ Possible |
| READ COMMITTED | ✓ Prevented | ✗ Possible | ✗ Possible |
| REPEATABLE READ | ✓ Prevented | ✓ Prevented | ✗ Possible |
| SERIALIZABLE | ✓ Prevented | ✓ Prevented | ✓ Prevented |

**My Choice:** READ COMMITTED (MySQL default)
- Prevents dirty reads
- Good performance
- Suitable for ETL workload

**4. Durability (Data Persists)**
```ini
# MySQL configuration ensures durability
[mysqld]
innodb_flush_log_at_trx_commit = 1  # Flush to disk on commit
innodb_flush_method = O_DIRECT       # Direct I/O
```

**Verification:**
```python
# After insert, verify data persists
insert_count = len(df)
connection.commit()

# Query to verify
result = connection.execute("SELECT COUNT(*) FROM variants")
db_count = result.fetchone()[0]

assert insert_count == db_count, "Data not persisted correctly"
```

---

## Python & Performance Questions

### Q4: Explain the Global Interpreter Lock (GIL) and how it affects your pipeline.

**Answer:**

**What is GIL:**
- Python's mechanism to ensure only one thread executes Python bytecode at a time
- Prevents race conditions in CPython's memory management
- Limits CPU-bound parallel processing

**Impact on My Pipeline:**

**CPU-Bound Tasks (Limited by GIL):**
```python
# VCF parsing - CPU intensive
# GIL means threads don't provide speedup
with ThreadPoolExecutor(max_workers=4) as executor:
    results = executor.map(parse_vcf_line, lines)
    # Only one thread runs at a time → No speedup
```

**I/O-Bound Tasks (Not limited by GIL):**
```python
# Database inserts - I/O intensive
# Threads work well because GIL released during I/O
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(insert_to_db, chunk) 
               for chunk in chunks]
    # Multiple threads can wait for I/O concurrently → Speedup!
```

**Solutions I Use:**

**1. Multiprocessing for CPU-bound:**
```python
from multiprocessing import Pool

# Each process has its own GIL
with Pool(processes=4) as pool:
    results = pool.map(parse_vcf_line, lines)
    # True parallelism → 4x speedup on 4 cores
```

**2. Vectorization (Best):**
```python
# Use NumPy/Pandas (C-based, releases GIL)
df['normalized'] = (df['position'] - df['position'].mean()) / df['position'].std()
# Runs in C, ignores GIL → Very fast
```

**3. Threading for I/O:**
```python
# Database operations, API calls
with ThreadPoolExecutor(max_workers=4) as executor:
    # GIL released during I/O wait
    futures = [executor.submit(fetch_from_api, gene) 
               for gene in genes]
```

**Performance Comparison:**
| Approach | 1M Variants | Speedup |
|----------|-------------|---------|
| Single-threaded | 60s | 1x |
| Multi-threaded (CPU) | 58s | 1.03x (minimal) |
| Multi-process (CPU) | 18s | 3.3x |
| Vectorized (Pandas) | 2s | 30x |

**My Strategy:**
1. Vectorize with Pandas/NumPy whenever possible (30x faster)
2. Use multiprocessing for remaining CPU-bound tasks
3. Use threading only for I/O-bound operations

---

### Q5: What's the difference between deep copy and shallow copy? Where does this matter in your project?

**Answer:**

**Shallow Copy:**
```python
import copy

original = {'data': [1, 2, 3]}
shallow = copy.copy(original)

shallow['data'].append(4)
print(original)  # {'data': [1, 2, 3, 4]} ← Modified!
print(shallow)   # {'data': [1, 2, 3, 4]}
```
- Copies object but not nested objects
- Both point to same nested data

**Deep Copy:**
```python
deep = copy.deepcopy(original)

deep['data'].append(5)
print(original)  # {'data': [1, 2, 3, 4]} ← Not modified
print(deep)      # {'data': [1, 2, 3, 4, 5]}
```
- Recursively copies all nested objects
- Completely independent copy

**Where This Matters in My Project:**

**1. DataFrame Operations:**
```python
# Pandas uses views (shallow) by default for performance
df = pd.DataFrame({'col': [1, 2, 3]})
subset = df[df['col'] > 1]  # View, not copy

subset['col'] = subset['col'] * 2  # SettingWithCopyWarning!

# Solution: Explicit copy
subset = df[df['col'] > 1].copy()
subset['col'] = subset['col'] * 2  # Safe
```

**2. Configuration Management:**
```python
# Don't modify original config
def process_with_custom_config(config, overrides):
    # Shallow copy would modify original
    custom_config = copy.deepcopy(config)
    custom_config.update(overrides)
    return process(custom_config)
```

**3. Batch Processing:**
```python
# Process chunks independently
for chunk in chunks:
    # Deep copy ensures modifications don't affect original
    processed = process(copy.deepcopy(chunk))
    insert_to_db(processed)
```

**Performance Consideration:**
```python
# Deep copy is expensive for large DataFrames
large_df = pd.DataFrame(np.random.rand(1000000, 10))

%timeit copy.deepcopy(large_df)  # 500ms
%timeit large_df.copy()          # 50ms (pandas optimized)

# Use pandas .copy() for DataFrames
df_copy = df.copy()  # Efficient
```

**My Approach:**
- Use Pandas `.copy()` for DataFrames (optimized)
- Use `deepcopy` for nested config objects
- Be aware of views vs copies in Pandas

---

## System Design Questions

### Q6: How would you implement caching for the enrichment APIs?

**Answer:**

**Problem:**
- ClinVar/DrugBank APIs are rate-limited (10 requests/second)
- Same genes queried repeatedly
- Network latency (100-500ms per request)

**Solution Architecture:**

**1. In-Memory Cache (LRU)**
```python
from functools import lru_cache

@lru_cache(maxsize=10000)
def fetch_gene_annotation(gene_symbol: str) -> dict:
    '''
    Fetch and cache gene annotation
    Cache stores 10,000 most recent genes
    '''
    response = requests.get(f'https://api.clinvar.com/gene/{gene_symbol}')
    return response.json()

# First call: Hits API (500ms)
result1 = fetch_gene_annotation('BRCA1')

# Second call: Returns from cache (<1ms)
result2 = fetch_gene_annotation('BRCA1')
```

**Benefits:**
- 500x faster for cached items
- Zero infrastructure needed
- Thread-safe

**Limitations:**
- Cache lost on restart
- Not shared across processes
- Limited size (memory)

**2. File-Based Cache**
```python
import json
import os
from datetime import datetime, timedelta

class FileCache:
    def __init__(self, cache_dir='cache', ttl_days=7):
        self.cache_dir = cache_dir
        self.ttl = timedelta(days=ttl_days)
        os.makedirs(cache_dir, exist_ok=True)
    
    def get(self, key: str) -> Optional[dict]:
        cache_file = os.path.join(self.cache_dir, f'{key}.json')
        
        if not os.path.exists(cache_file):
            return None
        
        # Check if expired
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
        if datetime.now() - file_time > self.ttl:
            return None
        
        with open(cache_file, 'r') as f:
            return json.load(f)
    
    def set(self, key: str, value: dict):
        cache_file = os.path.join(self.cache_dir, f'{key}.json')
        with open(cache_file, 'w') as f:
            json.dump(value, f)

# Usage
cache = FileCache()

def fetch_with_cache(gene):
    cached = cache.get(gene)
    if cached:
        logger.info(f"Cache hit: {gene}")
        return cached
    
    # Cache miss - fetch from API
    logger.info(f"Cache miss: {gene}")
    result = fetch_from_api(gene)
    cache.set(gene, result)
    return result
```

**Benefits:**
- Persists across restarts
- Shareable across processes
- TTL for freshness

**3. Database Cache**
```sql
CREATE TABLE api_cache (
    cache_key VARCHAR(100) PRIMARY KEY,
    cache_value JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_created (created_at)
);
```

```python
def fetch_with_db_cache(gene_symbol):
    # Check cache
    result = db.execute("""
        SELECT cache_value 
        FROM api_cache 
        WHERE cache_key = %s 
          AND created_at > DATE_SUB(NOW(), INTERVAL 7 DAY)
    """, (gene_symbol,))
    
    if result:
        return json.loads(result[0])
    
    # Fetch from API
    data = fetch_from_api(gene_symbol)
    
    # Store in cache
    db.execute("""
        INSERT INTO api_cache (cache_key, cache_value)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE 
            cache_value = VALUES(cache_value),
            created_at = CURRENT_TIMESTAMP
    """, (gene_symbol, json.dumps(data)))
    
    return data
```

**Benefits:**
- Persistent
- Shared across all processes
- Queryable (can analyze cache hits)

**4. Redis Cache (Production)**
```python
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def fetch_with_redis_cache(gene_symbol):
    cache_key = f'gene:{gene_symbol}'
    
    # Check cache
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Fetch from API
    data = fetch_from_api(gene_symbol)
    
    # Store with TTL (7 days)
    redis_client.setex(
        cache_key,
        timedelta(days=7),
        json.dumps(data)
    )
    
    return data
```

**Benefits:**
- Very fast (in-memory)
- Persistent
- Distributed
- TTL built-in
- Production-ready

**My Implementation:**

**Development:** File-based cache
```yaml
enrichment:
  cache_api_results: true
  cache_dir: 'cache/api'
  cache_ttl_days: 7
```

**Production:** Redis cache (future)

**Performance Impact:**
```
Without caching:
- 10,000 genes × 500ms = 5,000 seconds (83 minutes)
- Rate limited to 10/sec = 1,000 seconds (17 minutes)

With caching (90% hit rate):
- 1,000 API calls × 500ms = 500 seconds (8 minutes)
- 9,000 cache hits × 1ms = 9 seconds
- Total: ~9 minutes

Improvement: 9x faster
```

---

### Q7: How would you implement monitoring and alerting for this pipeline?

**Answer:**

**Monitoring Strategy:**

**1. Logging (Current Implementation)**
```python
# Structured logging
logger.info("Pipeline phase completed", extra={
    'phase': 'extraction',
    'duration_seconds': 45.2,
    'records_processed': 1000000,
    'status': 'success'
})

# Error tracking
logger.error("Database connection failed", extra={
    'host': 'localhost',
    'port': 3306,
    'retry_count': 3
}, exc_info=True)
```

**2. Metrics Collection**
```python
class PipelineMetrics:
    def __init__(self):
        self.metrics = {
            'variants_processed': 0,
            'genes_extracted': 0,
            'api_calls_made': 0,
            'errors_encountered': 0,
            'duration_seconds': 0
        }
    
    def record_metric(self, key, value):
        self.metrics[key] = value
        # Send to monitoring system
        self.send_to_prometheus(key, value)
    
    def send_to_prometheus(self, key, value):
        # Push to Prometheus pushgateway
        from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
        
        registry = CollectorRegistry()
        gauge = Gauge(key, 'Pipeline metric', registry=registry)
        gauge.set(value)
        
        push_to_gateway('localhost:9091', job='genomic_pipeline', registry=registry)

# Usage
metrics = PipelineMetrics()
metrics.record_metric('variants_processed', len(df))
```

**3. Health Checks**
```python
class HealthCheck:
    def check_database(self) -> bool:
        try:
            db.execute("SELECT 1")
            return True
        except Exception:
            return False
    
    def check_disk_space(self) -> bool:
        import shutil
        stat = shutil.disk_usage('/')
        free_gb = stat.free / (2**30)
        return free_gb > 10  # At least 10GB free
    
    def check_memory(self) -> bool:
        import psutil
        memory = psutil.virtual_memory()
        return memory.available / (2**30) > 2  # At least 2GB free
    
    def check_all(self) -> dict:
        return {
            'database': self.check_database(),
            'disk_space': self.check_disk_space(),
            'memory': self.check_memory(),
            'timestamp': datetime.now().isoformat()
        }

# Expose health endpoint
@app.get("/health")
def health():
    health_check = HealthCheck()
    status = health_check.check_all()
    
    if all(status.values()):
        return {"status": "healthy", "checks": status}
    else:
        return {"status": "unhealthy", "checks": status}, 503
```

**4. Alerting**
```python
class AlertManager:
    def __init__(self):
        self.email_config = load_email_config()
        self.slack_webhook = load_slack_webhook()
    
    def send_alert(self, severity, message, details=None):
        alert = {
            'severity': severity,  # critical, warning, info
            'message': message,
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'host': socket.gethostname()
        }
        
        if severity == 'critical':
            self.send_email(alert)
            self.send_slack(alert)
        elif severity == 'warning':
            self.send_slack(alert)
        
        # Always log
        logger.warning(f"Alert: {message}", extra=details)
    
    def send_email(self, alert):
        import smtplib
        from email.mime.text import MIMEText
        
        msg = MIMEText(json.dumps(alert, indent=2))
        msg['Subject'] = f"[{alert['severity'].upper()}] Pipeline Alert"
        msg['From'] = self.email_config['from']
        msg['To'] = self.email_config['to']
        
        with smtplib.SMTP(self.email_config['host']) as server:
            server.send_message(msg)
    
    def send_slack(self, alert):
        requests.post(self.slack_webhook, json={
            'text': f":rotating_light: *{alert['severity'].upper()}*\n{alert['message']}"
        })

# Usage
alert_manager = AlertManager()

try:
    run_pipeline()
except DatabaseConnectionError as e:
    alert_manager.send_alert('critical', 'Pipeline failed: Database connection', {
        'error': str(e),
        'phase': 'loading'
    })
except Exception as e:
    alert_manager.send_alert('warning', 'Pipeline error', {'error': str(e)})
```

**5. Dashboard (Grafana)**
```yaml
# Prometheus configuration
scrape_configs:
  - job_name: 'genomic_pipeline'
    static_configs:
      - targets: ['localhost:9090']
```

**Metrics to Monitor:**
- **Performance:** Processing time per phase, records/second
- **Resources:** CPU usage, memory usage, disk space
- **Quality:** Error rate, success rate, data quality scores
- **Business:** Variants processed, genes annotated, completeness

**Alert Rules:**
```yaml
# Alert if pipeline fails
- alert: PipelineFailed
  expr: pipeline_status == 0
  for: 5m
  annotations:
    summary: "Pipeline has failed"
    
# Alert if processing is slow
- alert: SlowProcessing
  expr: pipeline_duration_seconds > 3600
  annotations:
    summary: "Pipeline taking longer than 1 hour"

# Alert if disk space low
- alert: LowDiskSpace
  expr: disk_free_gb < 10
  annotations:
    summary: "Less than 10GB disk space remaining"
```

**Production Monitoring Stack:**
```
Application → Prometheus → Grafana → Alerts
           ↓
       CloudWatch/DataDog (optional)
```

This provides comprehensive visibility into pipeline health and performance.

---

This documentation provides deep technical knowledge needed for advanced interviews. Practice explaining these concepts clearly and demonstrating your understanding of the underlying principles.

