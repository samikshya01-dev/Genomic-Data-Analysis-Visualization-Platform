"""
Main ETL Pipeline Orchestrator
Coordinates the complete genomic data analysis workflow
"""
import argparse
import sys
import os
from typing import Optional
from datetime import datetime

# Add parent directory to path if running directly
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.etl import VCFExtractor, VCFTransformer, MySQLLoader, AnnotationEnricher
from src.analysis import VariantSummary, MutationAnalysis
from src.utils import get_logger, log_execution_time

logger = get_logger('main_pipeline')


class DatabaseConnectionError(Exception):
    """Custom exception for database connection failures"""
    pass


class GenomicPipeline:
    """Main pipeline orchestrator for genomic data analysis"""

    def __init__(self):
        """Initialize pipeline components"""
        self.extractor = VCFExtractor()
        self.transformer = VCFTransformer()
        self.loader = MySQLLoader()
        self.enricher = AnnotationEnricher()
        self.summary = VariantSummary()
        self.analyzer = MutationAnalysis()

    @log_execution_time
    def run_extraction(self, force: bool = False) -> str:
        """Run VCF extraction phase

        Args:
            force: Force re-download and re-extraction

        Returns:
            Path to extracted VCF file
        """
        logger.info("=" * 80)
        logger.info("PHASE 1: VCF EXTRACTION")
        logger.info("=" * 80)

        vcf_path = self.extractor.extract_all(
            force_download=force,
            force_extract=force
        )

        logger.info(f"✓ VCF extraction completed: {vcf_path}")
        return vcf_path

    @log_execution_time
    def run_transformation(self, max_rows: Optional[int] = None, use_vcfpy: bool = False):
        """Run VCF transformation phase

        Args:
            max_rows: Maximum number of rows to process (None for all)
            use_vcfpy: Use vcfpy library for parsing

        Returns:
            Tuple of (variants_df, genes_df)
        """
        logger.info("=" * 80)
        logger.info("PHASE 2: VCF TRANSFORMATION")
        logger.info("=" * 80)

        variants_df, genes_df = self.transformer.transform_all(
            use_vcfpy=use_vcfpy,
            max_rows=max_rows
        )

        logger.info(f"✓ Transformation completed: {len(variants_df)} variants, {len(genes_df)} genes")
        return variants_df, genes_df

    @log_execution_time
    def run_enrichment(self, enrich_descriptions: bool = False):
        """Run annotation enrichment phase

        Args:
            enrich_descriptions: Enrich with gene descriptions from Ensembl

        Returns:
            Tuple of (genes_df, drug_annotations_df)
        """
        logger.info("=" * 80)
        logger.info("PHASE 3: ANNOTATION ENRICHMENT")
        logger.info("=" * 80)

        genes_df, drug_annotations_df = self.enricher.enrich_all(
            enrich_descriptions=enrich_descriptions
        )

        logger.info(f"✓ Enrichment completed: {len(drug_annotations_df)} drug annotations")
        return genes_df, drug_annotations_df

    @log_execution_time
    def run_loading(self, drop_existing: bool = False):
        """Run database loading phase

        Args:
            drop_existing: Drop existing tables before loading
        """
        logger.info("=" * 80)
        logger.info("PHASE 4: DATABASE LOADING")
        logger.info("=" * 80)

        # Test connection first
        if not self.loader.db_config.test_connection():
            raise DatabaseConnectionError("Database connection test failed. Please check your configuration.")

        self.loader.load_all(drop_existing=drop_existing)

        # Show statistics
        counts = self.loader.get_table_counts()
        logger.info("✓ Database loading completed:")
        for table, count in counts.items():
            logger.info(f"  - {table}: {count:,} rows")

    @log_execution_time
    def run_analysis(self):
        """Run analysis and reporting phase"""
        logger.info("=" * 80)
        logger.info("PHASE 5: ANALYSIS & REPORTING")
        logger.info("=" * 80)

        # Generate summary statistics
        logger.info("Generating summary statistics...")
        summaries = self.summary.generate_all_summaries()
        logger.info(f"✓ Generated {len(summaries)} summary reports")

        # Generate mutation analysis report
        logger.info("Generating mutation analysis report...")
        report = self.analyzer.generate_mutation_report()

        # Save report
        import os
        output_dir = "data/processed"
        os.makedirs(output_dir, exist_ok=True)
        report_file = os.path.join(
            output_dir,
            f"mutation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        with open(report_file, 'w') as f:
            f.write(report)

        logger.info(f"✓ Analysis completed. Report saved to: {report_file}")

        return report

    @log_execution_time
    def run_full_pipeline(
        self,
        force_download: bool = False,
        max_rows: Optional[int] = None,
        drop_existing: bool = False,
        skip_enrichment: bool = False,
        skip_analysis: bool = False
    ):
        """Run the complete pipeline

        Args:
            force_download: Force re-download of VCF file
            max_rows: Maximum number of rows to process
            drop_existing: Drop existing database tables
            skip_enrichment: Skip enrichment phase
            skip_analysis: Skip analysis phase
        """
        start_time = datetime.now()

        logger.info("=" * 80)
        logger.info("GENOMIC DATA ANALYSIS PIPELINE")
        logger.info(f"Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)

        try:
            # Phase 1: Extraction
            self.run_extraction(force=force_download)

            # Phase 2: Transformation
            self.run_transformation(max_rows=max_rows, use_vcfpy=False)

            # Phase 3: Enrichment (optional)
            if not skip_enrichment:
                self.run_enrichment(enrich_descriptions=False)
            else:
                logger.info("Skipping enrichment phase")

            # Phase 4: Loading
            self.run_loading(drop_existing=drop_existing)

            # Phase 5: Analysis (optional)
            if not skip_analysis:
                self.run_analysis()
            else:
                logger.info("Skipping analysis phase")

            # Summary
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            logger.info("=" * 80)
            logger.info("PIPELINE COMPLETED SUCCESSFULLY")
            logger.info(f"Finished at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"Total duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
            logger.info("=" * 80)

            return True

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            logger.error("Please check the logs for more details")
            return False


def main():
    """Main entry point with command-line interface"""
    parser = argparse.ArgumentParser(
        description='Genomic Data Analysis & Visualization Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline
  python main.py --full
  
  # Run with limited rows (for testing)
  python main.py --full --max-rows 10000
  
  # Run individual phases
  python main.py --extract
  python main.py --transform
  python main.py --load
  python main.py --analyze
  
  # Force re-download and drop existing tables
  python main.py --full --force-download --drop-existing
        """
    )

    # Pipeline phases
    parser.add_argument('--full', action='store_true',
                       help='Run full pipeline (all phases)')
    parser.add_argument('--extract', action='store_true',
                       help='Run extraction phase only')
    parser.add_argument('--transform', action='store_true',
                       help='Run transformation phase only')
    parser.add_argument('--enrich', action='store_true',
                       help='Run enrichment phase only')
    parser.add_argument('--load', action='store_true',
                       help='Run loading phase only')
    parser.add_argument('--analyze', action='store_true',
                       help='Run analysis phase only')

    # Options
    parser.add_argument('--force-download', action='store_true',
                       help='Force re-download of VCF file')
    parser.add_argument('--max-rows', type=int, default=None,
                       help='Maximum number of rows to process (for testing)')
    parser.add_argument('--drop-existing', action='store_true',
                       help='Drop existing database tables before loading')
    parser.add_argument('--skip-enrichment', action='store_true',
                       help='Skip enrichment phase in full pipeline')
    parser.add_argument('--skip-analysis', action='store_true',
                       help='Skip analysis phase in full pipeline')
    parser.add_argument('--use-vcfpy', action='store_true',
                       help='Use vcfpy library for parsing (slower but more robust)')

    args = parser.parse_args()

    # Create pipeline
    pipeline = GenomicPipeline()

    try:
        # Run requested phase(s)
        if args.full:
            success = pipeline.run_full_pipeline(
                force_download=args.force_download,
                max_rows=args.max_rows,
                drop_existing=args.drop_existing,
                skip_enrichment=args.skip_enrichment,
                skip_analysis=args.skip_analysis
            )
            sys.exit(0 if success else 1)

        elif args.extract:
            pipeline.run_extraction(force=args.force_download)

        elif args.transform:
            pipeline.run_transformation(
                max_rows=args.max_rows,
                use_vcfpy=args.use_vcfpy
            )

        elif args.enrich:
            pipeline.run_enrichment(enrich_descriptions=False)

        elif args.load:
            pipeline.run_loading(drop_existing=args.drop_existing)

        elif args.analyze:
            pipeline.run_analysis()

        else:
            parser.print_help()
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("\nPipeline interrupted by user")
        sys.exit(1)

    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

