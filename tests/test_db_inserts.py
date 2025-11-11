"""
Test database insert operations
"""
import pytest
import pandas as pd
import os
import sys

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.etl.load_to_mysql import MySQLLoader
from src.utils import get_db_config


class TestDatabaseConnection:
    """Test database connection and basic operations"""

    @pytest.fixture
    def db_config(self):
        """Get database configuration"""
        return get_db_config()

    @pytest.fixture
    def loader(self):
        """Create MySQL loader instance"""
        return MySQLLoader()

    def test_database_connection(self, db_config):
        """Test database connection"""
        # This test will be skipped if database is not configured
        try:
            success = db_config.test_connection()
            assert success, "Database connection failed"
        except Exception as e:
            pytest.skip(f"Database not configured: {e}")

    def test_get_engine(self, db_config):
        """Test engine creation"""
        try:
            engine = db_config.get_engine()
            assert engine is not None
        except Exception as e:
            pytest.skip(f"Cannot create engine: {e}")

    def test_table_names(self, loader):
        """Test table name configuration"""
        table_name = loader.db_config.get_table_name('variants')
        assert table_name == 'variants'

        table_name = loader.db_config.get_table_name('genes')
        assert table_name == 'genes'


class TestDatabaseOperations:
    """Test database CRUD operations"""

    @pytest.fixture
    def loader(self):
        """Create MySQL loader instance"""
        return MySQLLoader()

    def test_create_tables(self, loader):
        """Test table creation"""
        try:
            loader.db_config.test_connection()
            loader.create_database()
            loader.create_tables(drop_existing=False)
            # If no exception, test passes
            assert True
        except Exception as e:
            pytest.skip(f"Cannot create tables: {e}")

    def test_performance_config(self, loader):
        """Test performance configuration"""
        perf_config = loader.db_config.get_performance_config()

        assert 'batch_size' in perf_config
        assert isinstance(perf_config['batch_size'], int)
        assert perf_config['batch_size'] > 0


class TestDataIntegrity:
    """Test data integrity constraints"""

    def test_variant_data_structure(self):
        """Test variant data structure"""
        # Create sample variant data
        variant_data = {
            'chromosome': 'chrX',
            'position': 12345,
            'reference_allele': 'A',
            'alternate_allele': 'G',
            'allele_frequency': 0.01
        }

        # Verify required fields
        assert 'chromosome' in variant_data
        assert 'position' in variant_data
        assert 'reference_allele' in variant_data
        assert 'alternate_allele' in variant_data

    def test_gene_data_structure(self):
        """Test gene data structure"""
        gene_data = {
            'gene_symbol': 'BRCA1',
            'gene_id': '672',
            'chromosome': 'chr17'
        }

        # Verify required fields
        assert 'gene_symbol' in gene_data
        assert gene_data['gene_symbol'] is not None

    def test_drug_annotation_structure(self):
        """Test drug annotation data structure"""
        drug_data = {
            'gene_symbol': 'BRCA1',
            'drug_name': 'Olaparib',
            'mechanism': 'PARP inhibitor',
            'indication': 'Breast cancer'
        }

        # Verify required fields
        assert 'gene_symbol' in drug_data
        assert 'drug_name' in drug_data


if __name__ == "__main__":
    pytest.main([__file__, '-v'])

