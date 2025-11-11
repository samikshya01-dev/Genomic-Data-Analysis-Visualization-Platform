#!/usr/bin/env python3
"""
Script to manually populate genes and drug_annotations tables with sample data
since the first 50,000 variants in the VCF don't contain gene information
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils import get_db_config, get_logger
import pandas as pd

logger = get_logger(__name__)

print("=" * 80)
print("POPULATING SAMPLE DATA FOR GENES AND DRUG_ANNOTATIONS")
print("=" * 80)
print()

# Sample genes data (common X chromosome genes)
genes_data = [
    {"gene_symbol": "DMD", "gene_id": "ENSG00000198947", "chromosome": "X", "description": "Dystrophin - mutations cause Duchenne muscular dystrophy"},
    {"gene_symbol": "FMR1", "gene_id": "ENSG00000102081", "chromosome": "X", "description": "Fragile X mental retardation 1 - causes Fragile X syndrome"},
    {"gene_symbol": "F8", "gene_id": "ENSG00000185010", "chromosome": "X", "description": "Coagulation factor VIII - mutations cause Hemophilia A"},
    {"gene_symbol": "F9", "gene_id": "ENSG00000101981", "chromosome": "X", "description": "Coagulation factor IX - mutations cause Hemophilia B"},
    {"gene_symbol": "GLA", "gene_id": "ENSG00000102393", "chromosome": "X", "description": "Galactosidase alpha - mutations cause Fabry disease"},
    {"gene_symbol": "MECP2", "gene_id": "ENSG00000169057", "chromosome": "X", "description": "Methyl-CpG binding protein 2 - causes Rett syndrome"},
    {"gene_symbol": "AR", "gene_id": "ENSG00000169083", "chromosome": "X", "description": "Androgen receptor - mutations cause androgen insensitivity"},
    {"gene_symbol": "COL4A5", "gene_id": "ENSG00000188153", "chromosome": "X", "description": "Collagen type IV alpha 5 - causes Alport syndrome"},
    {"gene_symbol": "G6PD", "gene_id": "ENSG00000160211", "chromosome": "X", "description": "Glucose-6-phosphate dehydrogenase deficiency"},
    {"gene_symbol": "OTC", "gene_id": "ENSG00000036473", "chromosome": "X", "description": "Ornithine transcarbamylase - urea cycle disorder"},
]

# Sample drug annotations
drug_annotations_data = [
    {
        "gene_symbol": "DMD",
        "drug_name": "Eteplirsen",
        "drug_bank_id": "DB11642",
        "mechanism": "Exon skipping therapy",
        "indication": "Duchenne muscular dystrophy",
        "drug_response": "Specific mutations responsive",
        "adverse_effects": "Upper respiratory infections, balance disorder",
        "clinical_trials": "NCT02255552",
        "source": "DrugBank"
    },
    {
        "gene_symbol": "F8",
        "drug_name": "Antihemophilic Factor",
        "drug_bank_id": "DB00025",
        "mechanism": "Factor VIII replacement",
        "indication": "Hemophilia A treatment",
        "drug_response": "Effective for F8 deficiency",
        "adverse_effects": "Inhibitor development, hypersensitivity",
        "clinical_trials": "NCT00000123",
        "source": "DrugBank"
    },
    {
        "gene_symbol": "F9",
        "drug_name": "Factor IX Complex",
        "drug_bank_id": "DB00100",
        "mechanism": "Factor IX replacement",
        "indication": "Hemophilia B treatment",
        "drug_response": "Effective for F9 deficiency",
        "adverse_effects": "Thrombotic events, allergic reactions",
        "clinical_trials": "NCT00000456",
        "source": "DrugBank"
    },
    {
        "gene_symbol": "GLA",
        "drug_name": "Agalsidase beta",
        "drug_bank_id": "DB00055",
        "mechanism": "Enzyme replacement",
        "indication": "Fabry disease treatment",
        "drug_response": "Reduces GL-3 accumulation",
        "adverse_effects": "Infusion reactions, headache",
        "clinical_trials": "NCT00001234",
        "source": "DrugBank"
    },
    {
        "gene_symbol": "G6PD",
        "drug_name": "Avoid: Primaquine",
        "drug_bank_id": "DB01087",
        "mechanism": "Contraindication",
        "indication": "G6PD deficiency - avoid antimalarials",
        "drug_response": "Risk of hemolysis",
        "adverse_effects": "Severe hemolytic anemia",
        "clinical_trials": "N/A",
        "source": "PharmGKB"
    },
    {
        "gene_symbol": "AR",
        "drug_name": "Bicalutamide",
        "drug_bank_id": "DB01128",
        "mechanism": "Androgen receptor antagonist",
        "indication": "Prostate cancer treatment",
        "drug_response": "AR mutations affect response",
        "adverse_effects": "Hot flashes, gynecomastia",
        "clinical_trials": "NCT00002345",
        "source": "DrugBank"
    },
    {
        "gene_symbol": "FMR1",
        "drug_name": "Mavoglurant",
        "drug_bank_id": "DB12345",
        "mechanism": "mGluR5 antagonist",
        "indication": "Fragile X syndrome (investigational)",
        "drug_response": "Behavioral improvements in trials",
        "adverse_effects": "Dizziness, nausea",
        "clinical_trials": "NCT01433354",
        "source": "ClinicalTrials.gov"
    },
    {
        "gene_symbol": "MECP2",
        "drug_name": "Trofinetide",
        "drug_bank_id": "DB15678",
        "mechanism": "IGF-1 analog",
        "indication": "Rett syndrome",
        "drug_response": "Improves symptoms",
        "adverse_effects": "Diarrhea, weight gain",
        "clinical_trials": "NCT02715115",
        "source": "FDA"
    },
]

try:
    # Get database connection
    db_config = get_db_config()

    print("[1/4] Testing database connection...")
    if not db_config.test_connection():
        print("✗ Database connection failed!")
        sys.exit(1)
    print("✓ Database connected successfully")
    print()

    # Create dataframes
    genes_df = pd.DataFrame(genes_data)
    drug_annotations_df = pd.DataFrame(drug_annotations_data)

    print(f"[2/4] Prepared sample data:")
    print(f"  - {len(genes_df)} genes")
    print(f"  - {len(drug_annotations_df)} drug annotations")
    print()

    # Get engine
    engine = db_config.get_engine()

    # Insert genes
    print("[3/4] Inserting genes into database...")
    genes_df.to_sql('genes', engine, if_exists='append', index=False)
    print(f"✓ Inserted {len(genes_df)} genes")
    print()

    # Insert drug annotations
    print("[4/4] Inserting drug annotations into database...")
    drug_annotations_df.to_sql('drug_annotations', engine, if_exists='append', index=False)
    print(f"✓ Inserted {len(drug_annotations_df)} drug annotations")
    print()

    # Verify counts
    print("Verifying table counts...")
    from sqlalchemy import text
    with engine.connect() as conn:
        tables = ['variants', 'genes', 'drug_annotations', 'mutation_summary']
        for table in tables:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = result.fetchone()[0]
            status = "✓" if count > 0 else "⚠"
            print(f"  {status} {table}: {count:,} rows")

    print()
    print("=" * 80)
    print("✓ SAMPLE DATA POPULATED SUCCESSFULLY!")
    print("=" * 80)
    print()
    print("Your database now has:")
    print("  ✓ variants table - populated with real VCF data")
    print("  ✓ genes table - populated with sample X chromosome genes")
    print("  ✓ drug_annotations table - populated with pharmacogenomic data")
    print("  ⚠ mutation_summary table - empty (requires genes in variants)")
    print()
    print("You can now connect Power BI to the database and create visualizations!")

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

