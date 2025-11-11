"""
Generate variant summary statistics and aggregations
"""
import pandas as pd
from pymongo import MongoClient
from typing import Dict, Optional

from ..utils import (
    get_logger,
    log_execution_time,
    load_config
)

logger = get_logger(__name__)


class VariantSummary:
    """Generate summary statistics for variants"""

    def __init__(self, config_path: str = "config/etl_config.yml", db_config_path: str = "config/db_config.yml"):
        """Initialize variant summary generator

        Args:
            config_path: Path to ETL configuration file
            db_config_path: Path to database configuration file
        """
        self.config = load_config(config_path)
        self.db_config = load_config(db_config_path)
        self.processed_path = self.config['paths']['processed_data']

        # MongoDB connection
        connection_string = self.db_config.get('connection_string', 'mongodb://localhost:27017/')
        self.client = MongoClient(connection_string)
        db_name = self.db_config['database']['database']
        self.db = self.client[db_name]

    @log_execution_time
    def get_variant_count_by_chromosome(self) -> pd.DataFrame:
        """Get variant count by chromosome

        Returns:
            DataFrame with chromosome and variant counts
        """
        logger.info("Calculating variant count by chromosome")

        pipeline = [
            {"$group": {
                "_id": "$chromosome",
                "variant_count": {"$sum": 1}
            }},
            {"$project": {
                "_id": 0,
                "chromosome": "$_id",
                "variant_count": 1
            }},
            {"$sort": {"chromosome": 1}}
        ]

        result = list(self.db.variants.aggregate(pipeline))
        df = pd.DataFrame(result)

        logger.info(f"Retrieved variant counts for {len(result)} chromosomes")
        return df

    @log_execution_time
    def get_variant_count_by_clinical_significance(self) -> pd.DataFrame:
        """Get variant count by clinical significance

        Returns:
            DataFrame with clinical significance and counts
        """
        logger.info("Calculating variant count by clinical significance")

        pipeline = [
            {"$match": {"clinical_significance": {"$ne": None, "$exists": True}}},
            {"$group": {
                "_id": "$clinical_significance",
                "variant_count": {"$sum": 1}
            }},
            {"$project": {
                "_id": 0,
                "clinical_significance": "$_id",
                "variant_count": 1
            }},
            {"$sort": {"variant_count": -1}}
        ]

        result = list(self.db.variants.aggregate(pipeline))
        df = pd.DataFrame(result)

        logger.info(f"Retrieved {len(result)} clinical significance categories")
        return df

    @log_execution_time
    def get_top_genes_by_variant_count(self, limit: int = 20) -> pd.DataFrame:
        """Get top genes by variant count

        Args:
            limit: Number of top genes to return

        Returns:
            DataFrame with top genes and variant counts
        """
        logger.info(f"Calculating top {limit} genes by variant count")

        pipeline = [
            {"$match": {"gene_symbol": {"$ne": None, "$exists": True}}},
            {"$group": {
                "_id": "$gene_symbol",
                "variant_count": {"$sum": 1},
                "avg_allele_frequency": {"$avg": "$allele_frequency"}
            }},
            {"$project": {
                "_id": 0,
                "gene_symbol": "$_id",
                "variant_count": 1,
                "avg_allele_frequency": 1
            }},
            {"$sort": {"variant_count": -1}},
            {"$limit": limit}
        ]

        result = list(self.db.variants.aggregate(pipeline))
        df = pd.DataFrame(result)

        logger.info(f"Retrieved top {len(result)} genes")
        return df

    @log_execution_time
    def get_pathogenic_variants_summary(self) -> pd.DataFrame:
        """Get summary of pathogenic and likely pathogenic variants

        Returns:
            DataFrame with pathogenic variant statistics
        """
        logger.info("Calculating pathogenic variants summary")

        pipeline = [
            {"$match": {
                "clinical_significance": {"$in": ["Pathogenic", "Likely pathogenic"]},
                "gene_symbol": {"$ne": None, "$exists": True}
            }},
            {"$group": {
                "_id": {
                    "gene_symbol": "$gene_symbol",
                    "chromosome": "$chromosome"
                },
                "pathogenic_count": {"$sum": 1},
                "avg_allele_frequency": {"$avg": "$allele_frequency"}
            }},
            {"$project": {
                "_id": 0,
                "gene_symbol": "$_id.gene_symbol",
                "chromosome": "$_id.chromosome",
                "pathogenic_count": 1,
                "avg_allele_frequency": 1
            }},
            {"$sort": {"pathogenic_count": -1}}
        ]

        result = list(self.db.variants.aggregate(pipeline))
        df = pd.DataFrame(result)

        logger.info(f"Retrieved pathogenic variants for {len(result)} genes")
        return df

    @log_execution_time
    def get_drug_associated_variants(self) -> pd.DataFrame:
        """Get variants associated with drug response

        Returns:
            DataFrame with drug-associated variants
        """
        logger.info("Calculating drug-associated variants")

        query = {
            "clinical_significance": "Drug response",
            "gene_symbol": {"$ne": None, "$exists": True}
        }
        projection = {
            "_id": 0,
            "gene_symbol": 1,
            "variant_id": 1,
            "clinical_significance": 1,
            "disease_name": 1
        }

        result = list(self.db.variants.find(query, projection).sort("gene_symbol", 1))
        df = pd.DataFrame(result)

        logger.info(f"Retrieved {len(result)} drug-associated variants")
        return df

    @log_execution_time
    def get_allele_frequency_distribution(self) -> pd.DataFrame:
        """Get allele frequency distribution statistics

        Returns:
            DataFrame with allele frequency statistics
        """
        logger.info("Calculating allele frequency distribution")

        pipeline = [
            {"$match": {"allele_frequency": {"$ne": None, "$exists": True}}},
            {"$group": {
                "_id": "$chromosome",
                "min_af": {"$min": "$allele_frequency"},
                "max_af": {"$max": "$allele_frequency"},
                "avg_af": {"$avg": "$allele_frequency"},
                "variant_count": {"$sum": 1}
            }},
            {"$project": {
                "_id": 0,
                "chromosome": "$_id",
                "min_af": 1,
                "max_af": 1,
                "avg_af": 1,
                "variant_count": 1
            }},
            {"$sort": {"chromosome": 1}}
        ]

        result = list(self.db.variants.aggregate(pipeline))
        df = pd.DataFrame(result)

        logger.info(f"Retrieved allele frequency stats for {len(result)} chromosomes")
        return df

    @log_execution_time
    def get_gene_drug_associations(self) -> pd.DataFrame:
        """Get gene-drug associations with variant counts

        Returns:
            DataFrame with gene-drug associations
        """
        logger.info("Calculating gene-drug associations")

        # Use MongoDB $lookup to join drug_annotations with variants
        pipeline = [
            {"$lookup": {
                "from": "variants",
                "localField": "gene_symbol",
                "foreignField": "gene_symbol",
                "as": "variants"
            }},
            {"$project": {
                "_id": 0,
                "gene_symbol": 1,
                "drug_name": 1,
                "mechanism": 1,
                "drug_response": 1,
                "variant_count": {"$size": "$variants"}
            }},
            {"$sort": {"gene_symbol": 1}}
        ]

        result = list(self.db.drug_annotations.aggregate(pipeline))
        df = pd.DataFrame(result)

        logger.info(f"Retrieved {len(result)} gene-drug associations")
        return df

    @log_execution_time
    def generate_all_summaries(self) -> Dict[str, pd.DataFrame]:
        """Generate all summary statistics

        Returns:
            Dictionary of summary DataFrames
        """
        logger.info("Generating all summary statistics")

        summaries = {
            'variants_by_chromosome': self.get_variant_count_by_chromosome(),
            'variants_by_clinical_sig': self.get_variant_count_by_clinical_significance(),
            'top_genes': self.get_top_genes_by_variant_count(),
            'pathogenic_variants': self.get_pathogenic_variants_summary(),
            'drug_associated_variants': self.get_drug_associated_variants(),
            'allele_frequency_dist': self.get_allele_frequency_distribution(),
            'gene_drug_associations': self.get_gene_drug_associations()
        }

        # Save all summaries to CSV
        import os
        for name, df in summaries.items():
            output_path = os.path.join(self.processed_path, f'{name}.csv')
            df.to_csv(output_path, index=False)
            logger.info(f"Saved {name} to {output_path}")

        logger.info("All summary statistics generated successfully")
        return summaries

    def print_summary_statistics(self):
        """Print summary statistics to console"""
        summaries = self.generate_all_summaries()

        print("\n" + "="*80)
        print("GENOMIC DATA SUMMARY STATISTICS")
        print("="*80)

        print("\n1. Variants by Chromosome:")
        print(summaries['variants_by_chromosome'].to_string(index=False))

        print("\n2. Variants by Clinical Significance:")
        print(summaries['variants_by_clinical_sig'].to_string(index=False))

        print("\n3. Top 10 Genes by Variant Count:")
        print(summaries['top_genes'].head(10).to_string(index=False))

        print("\n4. Pathogenic Variants Summary (Top 10):")
        print(summaries['pathogenic_variants'].head(10).to_string(index=False))

        print("\n5. Drug-Associated Variants:")
        print(f"Total: {len(summaries['drug_associated_variants'])}")
        if len(summaries['drug_associated_variants']) > 0:
            print(summaries['drug_associated_variants'].head(10).to_string(index=False))

        print("\n6. Gene-Drug Associations:")
        print(f"Total: {len(summaries['gene_drug_associations'])}")
        if len(summaries['gene_drug_associations']) > 0:
            print(summaries['gene_drug_associations'].head(10).to_string(index=False))

        print("\n" + "="*80)


def main():
    """Main execution function"""
    summary = VariantSummary()

    try:
        summary.print_summary_statistics()

    except Exception as e:
        logger.error(f"Error generating summary statistics: {e}")
        raise


if __name__ == "__main__":
    main()

