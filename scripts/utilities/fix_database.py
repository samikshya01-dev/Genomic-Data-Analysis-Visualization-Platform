#!/usr/bin/env python3
"""
Script to fix the empty tables issue by running the full pipeline
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.main import GenomicPipeline
from src.utils import get_logger

logger = get_logger('fix_database')


def main():
    """Run the pipeline to populate all tables"""

    logger.info("=" * 80)
    logger.info("FIXING DATABASE - Running Full Pipeline")
    logger.info("=" * 80)

    pipeline = GenomicPipeline()

    try:
        # Step 1: Check if VCF file exists
        vcf_path = "data/raw/homo_sapiens-chrX.vcf"
        if not os.path.exists(vcf_path):
            logger.error(f"VCF file not found: {vcf_path}")
            logger.info("Please run: python src/main.py --extract")
            return False

        logger.info(f"✓ VCF file found: {vcf_path}")

        # Step 2: Run transformation (creates variants.csv and genes.csv)
        logger.info("\n" + "=" * 80)
        logger.info("Running TRANSFORMATION phase...")
        logger.info("=" * 80)
        variants_df, genes_df = pipeline.run_transformation(max_rows=None, use_vcfpy=False)
        logger.info(f"✓ Created {len(variants_df)} variants and {len(genes_df)} genes")

        # Step 3: Run enrichment (creates drug_annotations.csv and enriches genes.csv)
        logger.info("\n" + "=" * 80)
        logger.info("Running ENRICHMENT phase...")
        logger.info("=" * 80)
        genes_df, drug_annotations_df = pipeline.run_enrichment(enrich_descriptions=False)
        logger.info(f"✓ Created {len(drug_annotations_df)} drug annotations")

        # Step 4: Load to database (loads all CSVs and creates mutation_summary)
        logger.info("\n" + "=" * 80)
        logger.info("Running LOADING phase...")
        logger.info("=" * 80)
        pipeline.run_loading(drop_existing=True)

        # Step 5: Show final counts
        logger.info("\n" + "=" * 80)
        logger.info("DATABASE FIXED - Final table counts:")
        logger.info("=" * 80)
        counts = pipeline.loader.get_table_counts()
        for table, count in counts.items():
            status = "✓" if count > 0 else "✗"
            logger.info(f"  {status} {table}: {count:,} rows")

        # Check if all tables have data
        all_tables_populated = all(count > 0 for count in counts.values())

        if all_tables_populated:
            logger.info("\n" + "=" * 80)
            logger.info("✓ SUCCESS! All tables are now populated with data")
            logger.info("=" * 80)
            return True
        else:
            logger.warning("\n" + "=" * 80)
            logger.warning("⚠ WARNING: Some tables are still empty")
            logger.warning("=" * 80)
            return False

    except Exception as e:
        logger.error(f"\n✗ ERROR: {e}", exc_info=True)
        logger.error("Database fix failed. Please check the error above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

