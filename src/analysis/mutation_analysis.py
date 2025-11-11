"""
Perform mutation frequency and distribution analysis
"""
import pandas as pd
import numpy as np
from pymongo import MongoClient
from typing import Dict, List, Optional
from collections import Counter

from ..utils import (
    get_logger,
    log_execution_time,
    load_config
)

logger = get_logger(__name__)


class MutationAnalysis:
    """Analyze mutation patterns and distributions"""

    def __init__(self, db_config_path: str = "config/db_config.yml"):
        """Initialize mutation analyzer

        Args:
            db_config_path: Path to database configuration file
        """
        self.db_config = load_config(db_config_path)

        # MongoDB connection
        connection_string = self.db_config.get('connection_string', 'mongodb://localhost:27017/')
        self.client = MongoClient(connection_string)
        db_name = self.db_config['database']['database']
        self.db = self.client[db_name]

    @log_execution_time
    def analyze_mutation_types(self) -> pd.DataFrame:
        """Analyze types of mutations (SNP, insertion, deletion, etc.)

        Returns:
            DataFrame with mutation type statistics
        """
        logger.info("Analyzing mutation types")

        # Query variants with both alleles
        query = {
            "reference_allele": {"$ne": None, "$exists": True},
            "alternate_allele": {"$ne": None, "$exists": True}
        }
        projection = {
            "_id": 0,
            "reference_allele": 1,
            "alternate_allele": 1
        }

        variants = list(self.db.variants.find(query, projection))
        df = pd.DataFrame(variants)

        # Classify mutation types
        def classify_mutation(row):
            ref = str(row['reference_allele'])
            alt = str(row['alternate_allele'])

            # Handle multiple alternates
            if ',' in alt:
                alt = alt.split(',')[0]

            ref_len = len(ref)
            alt_len = len(alt)

            if ref_len == 1 and alt_len == 1:
                return 'SNV'  # Single Nucleotide Variant
            elif ref_len > alt_len:
                return 'Deletion'
            elif ref_len < alt_len:
                return 'Insertion'
            else:
                return 'Complex'

        df['mutation_type'] = df.apply(classify_mutation, axis=1)

        # Count mutation types
        mutation_counts = df['mutation_type'].value_counts().reset_index()
        mutation_counts.columns = ['mutation_type', 'count']
        mutation_counts['percentage'] = (mutation_counts['count'] / len(df) * 100).round(2)

        logger.info(f"Analyzed {len(df)} mutations")
        return mutation_counts

    @log_execution_time
    def analyze_nucleotide_substitutions(self) -> pd.DataFrame:
        """Analyze nucleotide substitution patterns

        Returns:
            DataFrame with substitution patterns
        """
        logger.info("Analyzing nucleotide substitutions")

        # Query variants with both alleles
        query = {
            "reference_allele": {"$ne": None, "$exists": True},
            "alternate_allele": {"$ne": None, "$exists": True}
        }
        projection = {
            "_id": 0,
            "reference_allele": 1,
            "alternate_allele": 1
        }

        variants = list(self.db.variants.find(query, projection))
        df = pd.DataFrame(variants)

        # Filter for single nucleotide variants
        df = df[
            (df['reference_allele'].str.len() == 1) &
            (df['alternate_allele'].str.len() == 1)
        ]

        # Create substitution pattern
        df['substitution'] = df['reference_allele'] + '>' + df['alternate_allele']

        # Count substitutions
        substitution_counts = df['substitution'].value_counts().reset_index()
        substitution_counts.columns = ['substitution', 'count']
        substitution_counts['percentage'] = (
            substitution_counts['count'] / len(df) * 100
        ).round(2)

        # Classify as transition or transversion
        def classify_change(sub):
            transitions = ['A>G', 'G>A', 'C>T', 'T>C']
            return 'Transition' if sub in transitions else 'Transversion'

        substitution_counts['type'] = substitution_counts['substitution'].apply(classify_change)

        logger.info(f"Analyzed {len(df)} nucleotide substitutions")
        return substitution_counts

    @log_execution_time
    def analyze_position_distribution(self) -> pd.DataFrame:
        """Analyze distribution of variants across chromosomal positions

        Returns:
            DataFrame with position statistics
        """
        logger.info("Analyzing position distribution")

        # Use aggregation pipeline
        pipeline = [
            {"$group": {
                "_id": "$chromosome",
                "min_position": {"$min": "$position"},
                "max_position": {"$max": "$position"},
                "mean_position": {"$avg": "$position"},
                "variant_count": {"$sum": 1},
                "positions": {"$push": "$position"}
            }},
            {"$project": {
                "_id": 0,
                "chromosome": "$_id",
                "min_position": 1,
                "max_position": 1,
                "mean_position": 1,
                "variant_count": 1,
                "positions": 1
            }},
            {"$sort": {"chromosome": 1}}
        ]

        result = list(self.db.variants.aggregate(pipeline, allowDiskUse=True))

        # Calculate median manually (MongoDB doesn't have built-in median)
        for doc in result:
            positions = sorted(doc.pop('positions'))
            n = len(positions)
            if n % 2 == 0:
                doc['median_position'] = (positions[n//2 - 1] + positions[n//2]) / 2
            else:
                doc['median_position'] = positions[n//2]

        df = pd.DataFrame(result)

        logger.info(f"Analyzed position distribution for {len(df)} chromosomes")
        return df

    @log_execution_time
    def analyze_quality_scores(self) -> pd.DataFrame:
        """Analyze quality score distribution

        Returns:
            DataFrame with quality statistics
        """
        logger.info("Analyzing quality scores")

        query = {"quality": {"$ne": None, "$exists": True}}
        projection = {"_id": 0, "chromosome": 1, "quality": 1}

        variants = list(self.db.variants.find(query, projection))

        if not variants:
            logger.warning("No quality scores found in data")
            return pd.DataFrame()

        df = pd.DataFrame(variants)

        # Convert to numeric
        df['quality'] = pd.to_numeric(df['quality'], errors='coerce')
        df = df.dropna(subset=['quality'])

        # Calculate statistics
        stats = df.groupby('chromosome')['quality'].agg([
            ('min_quality', 'min'),
            ('max_quality', 'max'),
            ('mean_quality', 'mean'),
            ('median_quality', 'median'),
            ('count', 'count')
        ]).reset_index()

        logger.info(f"Analyzed quality scores for {len(df)} variants")
        return stats

    @log_execution_time
    def analyze_clinical_impact(self) -> Dict[str, pd.DataFrame]:
        """Analyze clinical impact of mutations

        Returns:
            Dictionary with various clinical impact analyses
        """
        logger.info("Analyzing clinical impact")

        # Query variants with clinical significance
        query = {"clinical_significance": {"$ne": None, "$exists": True}}
        projection = {
            "_id": 0,
            "gene_symbol": 1,
            "clinical_significance": 1,
            "disease_name": 1,
            "allele_frequency": 1
        }

        variants = list(self.db.variants.find(query, projection))
        df = pd.DataFrame(variants)

        results = {}

        # 1. Impact by gene
        gene_impact = df.groupby(['gene_symbol', 'clinical_significance']).size().reset_index(name='count')
        gene_impact = gene_impact.pivot_table(
            index='gene_symbol',
            columns='clinical_significance',
            values='count',
            fill_value=0
        ).reset_index()
        results['gene_impact'] = gene_impact

        # 2. Disease associations
        disease_counts = df[df['disease_name'].notna()].groupby('disease_name').size().reset_index(name='variant_count')
        disease_counts = disease_counts.sort_values('variant_count', ascending=False)
        results['disease_associations'] = disease_counts

        # 3. Pathogenicity vs allele frequency
        pathogenic_af = df[
            df['clinical_significance'].isin(['Pathogenic', 'Likely pathogenic'])
        ].copy()
        pathogenic_af = pathogenic_af[pathogenic_af['allele_frequency'].notna()]

        if len(pathogenic_af) > 0:
            af_stats = pathogenic_af['allele_frequency'].describe().to_frame()
            af_stats.columns = ['allele_frequency']
            results['pathogenic_af_stats'] = af_stats

        logger.info("Clinical impact analysis completed")
        return results


    @log_execution_time
    def generate_mutation_report(self) -> str:
        """Generate comprehensive mutation analysis report

        Returns:
            Report string
        """
        logger.info("Generating mutation analysis report")

        report_lines = []
        report_lines.append("="*80)
        report_lines.append("MUTATION ANALYSIS REPORT")
        report_lines.append("="*80)

        # 1. Mutation types
        mutation_types = self.analyze_mutation_types()
        report_lines.append("\n1. MUTATION TYPES")
        report_lines.append("-" * 40)
        report_lines.append(mutation_types.to_string(index=False))

        # 2. Nucleotide substitutions
        substitutions = self.analyze_nucleotide_substitutions()
        report_lines.append("\n\n2. NUCLEOTIDE SUBSTITUTION PATTERNS (Top 10)")
        report_lines.append("-" * 40)
        report_lines.append(substitutions.head(10).to_string(index=False))

        # Calculate transition/transversion ratio
        if len(substitutions) > 0:
            ts = substitutions[substitutions['type'] == 'Transition']['count'].sum()
            tv = substitutions[substitutions['type'] == 'Transversion']['count'].sum()
            if tv > 0:
                ts_tv_ratio = ts / tv
                report_lines.append(f"\nTransition/Transversion Ratio: {ts_tv_ratio:.2f}")

        # 3. Position distribution
        position_dist = self.analyze_position_distribution()
        report_lines.append("\n\n3. CHROMOSOMAL POSITION DISTRIBUTION")
        report_lines.append("-" * 40)
        report_lines.append(position_dist.to_string(index=False))

        # 4. Clinical impact
        clinical_impact = self.analyze_clinical_impact()

        if 'gene_impact' in clinical_impact:
            report_lines.append("\n\n4. CLINICAL IMPACT BY GENE (Top 10)")
            report_lines.append("-" * 40)
            report_lines.append(clinical_impact['gene_impact'].head(10).to_string(index=False))

        if 'disease_associations' in clinical_impact:
            report_lines.append("\n\n5. DISEASE ASSOCIATIONS (Top 10)")
            report_lines.append("-" * 40)
            report_lines.append(clinical_impact['disease_associations'].head(10).to_string(index=False))

        report_lines.append("\n" + "="*80)

        report = "\n".join(report_lines)
        logger.info("Mutation analysis report generated")

        return report


def main():
    """Main execution function"""
    analyzer = MutationAnalysis()

    try:
        report = analyzer.generate_mutation_report()
        print(report)

        # Save report to file
        import os
        from datetime import datetime

        output_dir = "data/processed"
        os.makedirs(output_dir, exist_ok=True)

        report_file = os.path.join(
            output_dir,
            f"mutation_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )

        with open(report_file, 'w') as f:
            f.write(report)

        logger.info(f"Report saved to {report_file}")

    except Exception as e:
        logger.error(f"Error in mutation analysis: {e}")
        raise


if __name__ == "__main__":
    main()

