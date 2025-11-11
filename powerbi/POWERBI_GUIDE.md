# Power BI Dashboard Guide

This guide provides instructions for creating comprehensive Power BI dashboards for genomic data visualization.

## 📊 Dashboard Setup

### Step 1: Connect to MySQL Database

1. Open Power BI Desktop
2. Click **Get Data** → **More** → **Database** → **MySQL database**
3. Enter connection details:
   - Server: `localhost:3306`
   - Database: `genomic_analysis`
4. Select **DirectQuery** or **Import** mode
   - **Import**: Better performance, but data is cached
   - **DirectQuery**: Real-time data, but slower queries

### Step 2: Import Tables

Select and import the following tables:
- `variants`
- `genes`
- `drug_annotations`
- `mutation_summary`

### Step 3: Create Relationships

Power BI should auto-detect relationships, but verify:
- `variants[gene_symbol]` → `genes[gene_symbol]`
- `variants[gene_symbol]` → `drug_annotations[gene_symbol]`
- `mutation_summary[gene_symbol]` → `genes[gene_symbol]`

## 📈 Dashboard 1: Mutation Frequency Overview

### Visualizations

#### 1. Variants by Chromosome (Bar Chart)
- **X-axis**: `variants[chromosome]`
- **Y-axis**: Count of `variants[id]`
- **Sort**: By chromosome number
- **Format**: Add data labels

#### 2. Clinical Significance Distribution (Pie Chart)
- **Legend**: `variants[clinical_significance]`
- **Values**: Count of `variants[id]`
- **Format**: Show percentages

#### 3. Top 20 Genes by Variant Count (Horizontal Bar Chart)
- **Y-axis**: `variants[gene_symbol]`
- **X-axis**: Count of `variants[id]`
- **Sort**: Descending by count
- **Filters**: Top 20

#### 4. Allele Frequency Distribution (Histogram)
- **X-axis**: `variants[allele_frequency]` (binned)
- **Y-axis**: Count
- **Bins**: 20
- **Format**: Log scale on Y-axis

### DAX Measures

```dax
// Total Variants
Total Variants = COUNT(variants[id])

// Pathogenic Variants
Pathogenic Variants = 
CALCULATE(
    COUNT(variants[id]),
    variants[clinical_significance] IN {"Pathogenic", "Likely pathogenic"}
)

// Pathogenic Percentage
Pathogenic % = 
DIVIDE(
    [Pathogenic Variants],
    [Total Variants],
    0
) * 100

// Average Allele Frequency
Avg Allele Frequency = AVERAGE(variants[allele_frequency])

// Unique Genes
Unique Genes = DISTINCTCOUNT(variants[gene_symbol])
```

### KPI Cards

Create card visualizations for:
- Total Variants
- Pathogenic Variants
- Pathogenic %
- Unique Genes
- Avg Allele Frequency

## 🧬 Dashboard 2: Drug-Biomarker Associations

### Visualizations

#### 1. Gene-Drug Network (Decomposition Tree)
- **Analyze**: Count of `drug_annotations[id]`
- **Explain by**: 
  - `drug_annotations[gene_symbol]`
  - `drug_annotations[drug_name]`
  - `drug_annotations[drug_response]`

#### 2. Drug Response Categories (Donut Chart)
- **Legend**: `drug_annotations[drug_response]`
- **Values**: Count of `drug_annotations[id]`

#### 3. Top Drugs by Gene Associations (Table)
- **Columns**:
  - `drug_annotations[drug_name]`
  - Count of `drug_annotations[gene_symbol]`
  - `drug_annotations[mechanism]`
  - `drug_annotations[indication]`
- **Sort**: By gene count descending

#### 4. Variants with Drug Associations (Scatter Plot)
- **X-axis**: `variants[allele_frequency]`
- **Y-axis**: Count of variants
- **Legend**: `drug_annotations[drug_response]`
- **Details**: `variants[gene_symbol]`

### DAX Measures

```dax
// Total Drug Annotations
Total Drug Annotations = COUNT(drug_annotations[id])

// Genes with Drug Targets
Genes with Drugs = DISTINCTCOUNT(drug_annotations[gene_symbol])

// Average Drugs per Gene
Avg Drugs per Gene = 
DIVIDE(
    COUNT(drug_annotations[id]),
    DISTINCTCOUNT(drug_annotations[gene_symbol]),
    0
)

// Variants with Drug Associations
Variants with Drugs = 
CALCULATE(
    COUNT(variants[id]),
    FILTER(
        variants,
        NOT(ISBLANK(RELATED(drug_annotations[drug_name])))
    )
)
```

### Filter Panel

Add slicers for:
- `drug_annotations[drug_response]`
- `drug_annotations[gene_symbol]`
- `variants[chromosome]`

## 🔬 Dashboard 3: Clinical Significance Analysis

### Visualizations

#### 1. Pathogenic vs Benign by Gene (Stacked Bar Chart)
- **Y-axis**: `mutation_summary[gene_symbol]`
- **X-axis**: Sum of variants
- **Legend**: `mutation_summary[clinical_significance]`
- **Filters**: Top 20 genes, only Pathogenic/Benign

#### 2. Clinical Significance Trend (Line Chart)
- **X-axis**: `variants[chromosome]`
- **Y-axis**: Count of variants
- **Legend**: `variants[clinical_significance]`

#### 3. Disease Associations (Word Cloud)
- **Category**: `variants[disease_name]`
- **Values**: Count of variants
- **Filters**: Exclude null values

#### 4. Quality Score Distribution (Box Plot)
- **Category**: `variants[chromosome]`
- **Values**: `variants[quality]`
- **Filters**: Quality > 0

### DAX Measures

```dax
// Benign Variants
Benign Variants = 
CALCULATE(
    COUNT(variants[id]),
    variants[clinical_significance] IN {"Benign", "Likely benign"}
)

// Uncertain Significance
Uncertain Variants = 
CALCULATE(
    COUNT(variants[id]),
    variants[clinical_significance] = "Uncertain significance"
)

// Clinical Significance Ratio
Pathogenic to Benign Ratio = 
DIVIDE(
    [Pathogenic Variants],
    [Benign Variants],
    0
)

// High Quality Variants
High Quality Variants = 
CALCULATE(
    COUNT(variants[id]),
    variants[quality] > 30
)
```

## 🎨 Dashboard 4: Mutation Hotspots

### Visualizations

#### 1. Chromosomal Position Heat Map
- **Rows**: `variants[chromosome]`
- **Columns**: `variants[position]` (binned by 10MB)
- **Values**: Count of variants
- **Color**: Gradient from blue (low) to red (high)

#### 2. Gene Mutation Density (Treemap)
- **Group**: `variants[gene_symbol]`
- **Values**: Count of variants
- **Color saturation**: `variants[pathogenic_count]`

#### 3. Mutation Type Distribution (Stacked Column)
- Create calculated column for mutation type:

```dax
Mutation Type = 
SWITCH(
    TRUE(),
    LEN(variants[reference_allele]) = 1 && LEN(variants[alternate_allele]) = 1, "SNV",
    LEN(variants[reference_allele]) > LEN(variants[alternate_allele]), "Deletion",
    LEN(variants[reference_allele]) < LEN(variants[alternate_allele]), "Insertion",
    "Complex"
)
```

- **X-axis**: `variants[chromosome]`
- **Y-axis**: Count
- **Legend**: `Mutation Type`

#### 4. Allele Frequency by Clinical Significance (Violin Plot)
- **Category**: `variants[clinical_significance]`
- **Values**: `variants[allele_frequency]`

### DAX Measures

```dax
// SNV Count
SNV Count = 
CALCULATE(
    COUNT(variants[id]),
    variants[Mutation Type] = "SNV"
)

// Indel Count
Indel Count = 
CALCULATE(
    COUNT(variants[id]),
    variants[Mutation Type] IN {"Insertion", "Deletion"}
)

// Transition/Transversion Ratio
// (Would require additional calculated columns for nucleotide classification)
```

## 🎯 Dashboard 5: Executive Summary

### Layout

Create a single-page executive dashboard with:

#### Top Row - Key Metrics (Cards)
- Total Variants
- Total Genes Analyzed
- Pathogenic Variants
- Drug Targets Identified
- Avg Allele Frequency

#### Middle Row - Primary Visualizations
- **Left**: Variants by Chromosome (Bar Chart)
- **Center**: Clinical Significance Distribution (Donut Chart)
- **Right**: Top 10 Genes (Bar Chart)

#### Bottom Row - Insights
- **Left**: Pathogenic Variants by Gene (Table)
- **Right**: Gene-Drug Associations (Table)

### Navigation

Add buttons to navigate between dashboards:
```dax
// Create bookmark for each dashboard
// Add button with action: Bookmark → [Dashboard Name]
```

## 📱 Mobile Layout

Configure mobile-optimized layouts:

1. View → Mobile Layout
2. Rearrange visualizations for portrait mode
3. Prioritize key metrics at the top
4. Use smaller visualizations for mobile

## 🔄 Refresh Configuration

### Scheduled Refresh (Power BI Service)

1. Publish dashboard to Power BI Service
2. Go to dataset settings
3. Configure scheduled refresh:
   - **Frequency**: Daily or Weekly
   - **Time**: After ETL pipeline runs (e.g., 3 AM)
   - **Time zone**: Your local time zone

### Gateway Configuration

For on-premises MySQL:
1. Install Power BI Gateway
2. Configure data source connection
3. Set up credentials
4. Test connection

## 🎨 Formatting Best Practices

### Color Schemes

#### Clinical Significance Colors
```
Pathogenic: #D32F2F (Red)
Likely Pathogenic: #F57C00 (Orange)
Uncertain Significance: #FBC02D (Yellow)
Likely Benign: #7CB342 (Light Green)
Benign: #388E3C (Green)
Drug Response: #1976D2 (Blue)
```

#### Chromosome Colors
Use a gradient or categorical colors for chromosomes 1-22, X, Y, M.

### Font Standards
- **Title**: Segoe UI, 14pt, Bold
- **Headers**: Segoe UI, 12pt, Semibold
- **Body**: Segoe UI, 10pt, Regular
- **KPIs**: Segoe UI, 24pt, Bold

### Theme
Apply consistent theme across all dashboards:
1. View → Themes
2. Customize theme or import JSON
3. Apply to all pages

## 📊 Performance Optimization

### Tips for Large Datasets

1. **Use aggregated tables**
   - Import `mutation_summary` instead of querying `variants` directly
   - Create additional aggregation tables if needed

2. **Optimize DAX queries**
   - Use SUMMARIZE instead of multiple FILTERs
   - Pre-calculate complex measures

3. **Reduce cardinality**
   - Group rare clinical significance values into "Other"
   - Bin continuous variables (position, allele frequency)

4. **Enable query reduction**
   - File → Options → Query reduction
   - Apply slicers with button click

## 🔒 Security & Sharing

### Row-Level Security (RLS)

If needed, implement RLS for multi-tenant scenarios:

```dax
// Create role: Researcher
[gene_symbol] IN {"BRCA1", "BRCA2", "TP53"}

// Create role: Institution A
[chromosome] IN {"chr1", "chr2", "chr3"}
```

### Sharing Options

1. **Publish to Workspace**: Share with team
2. **Create App**: Distribute to broader audience
3. **Embed**: Integrate into web applications
4. **Export**: PDF, PowerPoint, or Excel

## 📚 Additional Resources

- [Power BI Documentation](https://docs.microsoft.com/power-bi/)
- [DAX Guide](https://dax.guide/)
- [Power BI Community](https://community.powerbi.com/)
- [Genomic Data Visualization Best Practices](https://www.ensembl.org/info/website/tutorials/index.html)

## 🐛 Troubleshooting

### Common Issues

**Issue**: Connection timeout
- **Solution**: Increase timeout in Power BI settings or use Import mode

**Issue**: Poor performance with large dataset
- **Solution**: Use aggregated tables and DirectQuery for large tables

**Issue**: Relationships not working
- **Solution**: Verify gene_symbol column has same data type in all tables

**Issue**: Blank visualizations
- **Solution**: Check for NULL values and add filters to exclude them

---

For questions or improvements to this guide, please contact the project team.

