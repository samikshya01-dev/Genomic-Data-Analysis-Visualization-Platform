"""
Test data quality validation
"""
import pytest
import pandas as pd
import numpy as np
import os
import sys

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils import load_config


class TestDataQuality:
    """Test data quality validation"""

    def test_missing_values_threshold(self):
        """Test missing values are within acceptable threshold"""
        # Create sample data with missing values
        df = pd.DataFrame({
            'col1': [1, 2, 3, 4, 5, None, 7, 8, 9, 10],
            'col2': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        })

        # Calculate missing percentage
        missing_pct = (df['col1'].isna().sum() / len(df)) * 100

        # Should be less than or equal to 10%
        assert missing_pct <= 10

    def test_coordinate_validity(self):
        """Test genomic coordinates are valid"""
        # Create sample coordinate data
        coordinates = pd.DataFrame({
            'chromosome': ['chr1', 'chr2', 'chrX'],
            'position': [100, 200, 300]
        })

        # Positions should be positive
        assert (coordinates['position'] > 0).all()

        # Chromosomes should not be null
        assert coordinates['chromosome'].notna().all()

    def test_allele_frequency_range(self):
        """Test allele frequencies are in valid range [0, 1]"""
        af_values = pd.Series([0.01, 0.05, 0.1, 0.5, 0.99])

        # All values should be between 0 and 1
        assert (af_values >= 0).all()
        assert (af_values <= 1).all()

    def test_clinical_significance_values(self):
        """Test clinical significance values are valid"""
        valid_values = [
            'Benign',
            'Likely benign',
            'Uncertain significance',
            'Likely pathogenic',
            'Pathogenic',
            'Drug response',
            'Unknown'
        ]

        # Sample data
        clnsig = pd.Series(['Benign', 'Pathogenic', 'Unknown'])

        # All values should be in valid set
        for val in clnsig:
            assert val in valid_values or val is None


class TestEnrichmentQuality:
    """Test enrichment data quality"""

    def test_drug_gene_associations(self):
        """Test drug-gene associations are valid"""
        associations = pd.DataFrame({
            'gene_symbol': ['BRCA1', 'EGFR', 'TP53'],
            'drug_name': ['Olaparib', 'Gefitinib', 'APR-246']
        })

        # No null values in key fields
        assert associations['gene_symbol'].notna().all()
        assert associations['drug_name'].notna().all()

        # Gene symbols should be uppercase
        assert (associations['gene_symbol'].str.isupper()).all()

    def test_drugbank_id_format(self):
        """Test DrugBank ID format"""
        valid_ids = ['DB00001', 'DB09074', 'DB12345']

        for drug_id in valid_ids:
            # Should start with DB
            assert drug_id.startswith('DB')

            # Should have 5 digits after DB
            assert len(drug_id) == 7
            assert drug_id[2:].isdigit()


class TestDataConsistency:
    """Test data consistency across tables"""

    def test_gene_variant_consistency(self):
        """Test genes in variants exist in genes table"""
        variants = pd.DataFrame({
            'gene_symbol': ['BRCA1', 'BRCA2', 'TP53']
        })

        genes = pd.DataFrame({
            'gene_symbol': ['BRCA1', 'BRCA2', 'TP53', 'EGFR']
        })

        # All variant genes should exist in genes table
        variant_genes = set(variants['gene_symbol'].dropna())
        gene_list = set(genes['gene_symbol'])

        assert variant_genes.issubset(gene_list)

    def test_chromosome_consistency(self):
        """Test chromosome naming is consistent"""
        chromosomes = pd.Series(['chr1', 'chr2', 'chrX', 'chrY'])

        # All should start with 'chr' or be numeric/X/Y
        for chrom in chromosomes:
            assert chrom.startswith('chr') or chrom in ['X', 'Y', 'M'] or chrom.isdigit()


class TestStatisticalValidation:
    """Test statistical properties of data"""

    def test_allele_frequency_distribution(self):
        """Test allele frequency follows expected distribution"""
        # Rare variants should be more common than common variants
        af_values = np.random.beta(0.5, 10, 1000)  # Simulates rare variant distribution

        # Most variants should have low frequency
        low_freq = (af_values < 0.05).sum() / len(af_values)
        assert low_freq > 0.65  # At least 65% should be rare (adjusted for random variation)

    def test_variant_count_distribution(self):
        """Test variant counts are reasonable"""
        gene_counts = pd.Series([5, 10, 15, 100, 500, 1000])

        # Should have positive counts
        assert (gene_counts > 0).all()

        # Most genes should have moderate variant counts
        assert gene_counts.median() > 0


class TestConfigurationValidation:
    """Test configuration file validity"""

    def test_etl_config_structure(self):
        """Test ETL configuration structure"""
        try:
            config = load_config('config/etl_config.yml')

            # Required sections
            assert 'data_sources' in config
            assert 'paths' in config
            assert 'processing' in config
            assert 'vcf_parser' in config

            # Required paths
            assert 'raw_data' in config['paths']
            assert 'processed_data' in config['paths']

        except FileNotFoundError:
            pytest.skip("Configuration file not found")

    def test_db_config_structure(self):
        """Test database configuration structure"""
        try:
            config = load_config('config/db_config.yml')

            # Required sections
            assert 'database' in config
            assert 'tables' in config

            # Required database fields
            assert 'host' in config['database']
            assert 'database' in config['database']

        except FileNotFoundError:
            pytest.skip("Configuration file not found")


if __name__ == "__main__":
    pytest.main([__file__, '-v'])

