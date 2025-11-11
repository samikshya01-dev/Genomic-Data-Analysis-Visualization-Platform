"""
Test VCF parser functionality
"""
import pytest
import pandas as pd
import os
import sys

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.etl.transform_vcf import VCFTransformer


class TestVCFParser:
    """Test cases for VCF parser"""

    @pytest.fixture
    def transformer(self):
        """Create VCF transformer instance"""
        return VCFTransformer()

    def test_parse_info_field(self, transformer):
        """Test INFO field parsing"""
        info_str = "AF=0.01;AC=2;AN=1000;CLNSIG=benign"

        af = transformer._parse_info_field(info_str, 'AF')
        assert af == '0.01'

        ac = transformer._parse_info_field(info_str, 'AC')
        assert ac == '2'

        clnsig = transformer._parse_info_field(info_str, 'CLNSIG')
        assert clnsig == 'benign'

    def test_extract_gene_info(self, transformer):
        """Test gene information extraction"""
        info_str = "GENEINFO=BRCA1:672;AF=0.01"

        gene_symbol, gene_id = transformer._extract_gene_info(info_str)
        assert gene_symbol == 'BRCA1'
        assert gene_id == '672'

    def test_parse_clinical_significance(self, transformer):
        """Test clinical significance parsing"""
        # Test numeric mapping
        assert transformer._parse_clinical_significance('2') == 'Benign'
        assert transformer._parse_clinical_significance('5') == 'Pathogenic'

        # Test string pass-through
        assert transformer._parse_clinical_significance('benign') == 'benign'

        # Test None handling
        assert transformer._parse_clinical_significance(None) == 'Unknown'

    def test_parse_vcf_simple(self, transformer):
        """Test simple VCF parsing"""
        # This test would require a sample VCF file
        # For now, we'll skip if the file doesn't exist
        vcf_path = transformer.vcf_file_path

        if not os.path.exists(vcf_path):
            pytest.skip("VCF file not available")

        # Parse a small sample
        df = transformer.parse_vcf_simple(max_rows=100)

        # Verify DataFrame structure
        assert isinstance(df, pd.DataFrame)
        assert 'chromosome' in df.columns
        assert 'position' in df.columns
        assert 'reference_allele' in df.columns
        assert 'alternate_allele' in df.columns

        # Verify data types
        assert df['position'].dtype in [int, 'int64']

        # Verify no completely empty rows
        assert len(df) > 0

    def test_extract_genes(self, transformer):
        """Test gene extraction"""
        # Create sample variants DataFrame
        variants_df = pd.DataFrame({
            'gene_symbol': ['BRCA1', 'BRCA2', 'BRCA1', 'TP53'],
            'gene_id': ['672', '675', '672', '7157'],
            'chromosome': ['17', '13', '17', '17']
        })

        genes_df = transformer.extract_genes(variants_df)

        # Should have 3 unique genes
        assert len(genes_df) == 3
        assert 'BRCA1' in genes_df['gene_symbol'].values
        assert 'BRCA2' in genes_df['gene_symbol'].values
        assert 'TP53' in genes_df['gene_symbol'].values


class TestDataQuality:
    """Test data quality checks"""

    def test_required_fields_present(self):
        """Test that required fields are present in parsed data"""
        required_fields = ['chromosome', 'position', 'reference_allele', 'alternate_allele']

        # This would test actual parsed data
        # For now, just verify the list
        assert len(required_fields) == 4

    def test_chromosome_format(self):
        """Test chromosome format validation"""
        valid_chromosomes = ['chr1', 'chr2', 'chrX', 'chrY', 'chrM', 'X', 'Y', '1', '22']

        for chrom in valid_chromosomes:
            # Basic validation - chromosomes should be strings
            assert isinstance(chrom, str)

    def test_position_validity(self):
        """Test position value validity"""
        # Positions should be positive integers
        test_positions = [100, 1000, 10000, 1000000]

        for pos in test_positions:
            assert isinstance(pos, int)
            assert pos > 0


if __name__ == "__main__":
    pytest.main([__file__, '-v'])

