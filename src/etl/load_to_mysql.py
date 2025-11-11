"""
Load transformed data into MongoDB database
Optimized for high-performance bulk inserts and queries
"""
import pandas as pd
import numpy as np
from pymongo import MongoClient, ASCENDING, DESCENDING, IndexModel
from pymongo.errors import BulkWriteError
from typing import Optional, List, Dict, Any

from ..utils import (
    get_logger,
    log_execution_time,
    load_config
)

logger = get_logger(__name__)



class MongoDBLoader:
    """Load data into MongoDB database with optimized bulk operations"""

    def __init__(self, config_path: str = "config/etl_config.yml", db_config_path: str = "config/db_config.yml"):
        """Initialize MongoDB loader

        Args:
            config_path: Path to ETL configuration file
            db_config_path: Path to database configuration file
        """
        self.etl_config = load_config(config_path)
        self._db_config = load_config(db_config_path)
        self.client = None
        self.db = None

        # Get performance settings
        self.perf_config = self._db_config.get('performance', {})
        self.batch_size = self.perf_config.get('batch_size', 50000)

        # Get file paths
        self.variants_csv = self.etl_config['paths']['variants_csv']
        self.genes_csv = self.etl_config['paths']['genes_csv']
        self.drug_annotations_csv = self.etl_config['paths'].get('drug_annotations_csv')

    def _get_client(self):
        """Get MongoDB client connection with ultra-fast settings"""
        if self.client is None:
            connection_string = self._db_config.get('connection_string', 'mongodb://localhost:27017/')
            logger.info(f"Connecting to MongoDB: {connection_string}")

            # Get write concern settings for performance
            write_concern = self._db_config.get('performance', {}).get('write_concern', 0)

            # Connect with maximum performance settings
            self.client = MongoClient(
                connection_string,
                w=write_concern,           # Write concern: 0 = fastest (no ack)
                journal=False,             # No journaling
                maxPoolSize=200,           # Large connection pool
                minPoolSize=50,            # Keep connections ready
                maxIdleTimeMS=300000,      # Keep connections alive
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000,
                socketTimeoutMS=60000,
                retryWrites=False,         # No retry overhead
                compressors='snappy,zlib'  # Enable compression
            )

            # Get database
            db_name = self._db_config['database']['database']
            self.db = self.client[db_name]
            logger.info(f"Connected to database: {db_name}")
            logger.info(f"Write concern: {write_concern} (0=fastest, no acknowledgment)")
            logger.info(f"Connection pool: 50-200 connections")

        return self.client

    def _get_database(self):
        """Get MongoDB database instance"""
        if self.db is None:
            self._get_client()
        return self.db

    def test_connection(self):
        """Test MongoDB connection"""
        try:
            client = self._get_client()
            # Ping the database
            client.admin.command('ping')
            logger.info("MongoDB connection successful")
            return True
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            return False

    @log_execution_time
    def create_database(self):
        """Create database if it doesn't exist (MongoDB creates automatically)"""
        logger.info("Ensuring database exists")
        db = self._get_database()
        logger.info(f"Database '{db.name}' ready")

    @log_execution_time
    def create_collections(self, drop_existing: bool = False):
        """Create collections with indexes

        Args:
            drop_existing: Drop existing collections before creating
        """
        logger.info("Creating MongoDB collections with indexes")
        db = self._get_database()

        collections_config = self._db_config.get('collections', {})
        collection_names = [
            collections_config.get('variants', 'variants'),
            collections_config.get('genes', 'genes'),
            collections_config.get('drug_annotations', 'drug_annotations'),
            collections_config.get('mutation_summary', 'mutation_summary')
        ]

        for coll_name in collection_names:
            if drop_existing and coll_name in db.list_collection_names():
                logger.warning(f"Dropping existing collection: {coll_name}")
                db[coll_name].drop()

            # MongoDB creates collections automatically, but we'll create indexes
            logger.info(f"Collection '{coll_name}' ready")

        logger.info("Collections created successfully")

    @log_execution_time
    def create_indexes(self):
        """Create indexes for optimal query performance"""
        logger.info("Creating indexes for optimal performance")
        db = self._get_database()

        # Variants collection indexes
        variants_coll = db['variants']
        variants_indexes = [
            IndexModel([("chromosome", ASCENDING)]),
            IndexModel([("position", ASCENDING)]),
            IndexModel([("variant_id", ASCENDING)]),
            IndexModel([("gene_symbol", ASCENDING)]),
            IndexModel([("clinical_significance", ASCENDING)]),
            IndexModel([("chromosome", ASCENDING), ("position", ASCENDING)]),
            IndexModel([("gene_symbol", ASCENDING), ("clinical_significance", ASCENDING)])
        ]
        variants_coll.create_indexes(variants_indexes)
        logger.info("Created indexes for variants collection")

        # Genes collection indexes
        genes_coll = db['genes']
        genes_indexes = [
            IndexModel([("gene_symbol", ASCENDING)], unique=True),
            IndexModel([("gene_id", ASCENDING)]),
            IndexModel([("chromosome", ASCENDING)])
        ]
        genes_coll.create_indexes(genes_indexes)
        logger.info("Created indexes for genes collection")

        # Drug annotations collection indexes
        drug_coll = db['drug_annotations']
        drug_indexes = [
            IndexModel([("gene_symbol", ASCENDING)]),
            IndexModel([("drug_name", ASCENDING)]),
            IndexModel([("gene_symbol", ASCENDING), ("drug_name", ASCENDING)])
        ]
        drug_coll.create_indexes(drug_indexes)
        logger.info("Created indexes for drug_annotations collection")

        # Mutation summary collection indexes
        summary_coll = db['mutation_summary']
        summary_indexes = [
            IndexModel([("chromosome", ASCENDING)]),
            IndexModel([("gene_symbol", ASCENDING)]),
            IndexModel([("clinical_significance", ASCENDING)])
        ]
        summary_coll.create_indexes(summary_indexes)
        logger.info("Created indexes for mutation_summary collection")

        logger.info("All indexes created successfully")

    def _convert_to_mongo_doc(self, row: pd.Series) -> Dict[str, Any]:
        """Convert pandas row to MongoDB document, handling NaN values

        Args:
            row: Pandas series representing a row

        Returns:
            Dictionary ready for MongoDB insertion
        """
        doc = row.to_dict()

        # Convert NaN/None values to None (MongoDB null)
        for key, value in doc.items():
            if pd.isna(value):
                doc[key] = None
            elif isinstance(value, (np.integer, np.floating)):
                doc[key] = value.item()  # Convert numpy types to Python types

        return doc

    @log_execution_time
    def load_variants(self, csv_path: Optional[str] = None):
        """Load variants from CSV to MongoDB using RADICAL optimizations

        Args:
            csv_path: Path to variants CSV file
        """
        if csv_path is None:
            csv_path = self.variants_csv

        logger.info(f"Loading variants from {csv_path}")
        logger.info(f"RADICAL OPTIMIZATION MODE - Maximum speed!")
        logger.info(f"Batch size: {self.batch_size:,}")

        db = self._get_database()
        variants_coll = db['variants']

        import os
        file_size_mb = os.path.getsize(csv_path) / (1024 * 1024)
        logger.info(f"File size: {file_size_mb:.1f} MB")

        # RADICAL OPTIMIZATION 1: Use larger chunks for big files
        if file_size_mb > 1000:  # > 1GB
            chunk_size = 500000  # 500k rows per chunk
            logger.info(f"Large file detected - using 500k row chunks")
        else:
            chunk_size = self.batch_size

        # RADICAL OPTIMIZATION 2: Read CSV with optimized settings
        chunk_iterator = pd.read_csv(
            csv_path,
            chunksize=chunk_size,
            low_memory=False,
            engine='c',  # Use C engine (faster)
            na_filter=False  # Disable NA filtering (faster)
        )

        total_rows = 0
        chunk_num = 0

        logger.info("Starting ultra-fast chunked loading...")
        logger.info("Optimizations: C engine, no NA filter, w=0 (fire-and-forget)")

        for chunk in chunk_iterator:
            chunk_num += 1

            # RADICAL OPTIMIZATION 3: Direct dict conversion without fillna
            # MongoDB handles None/NaN natively, no need to process
            documents = chunk.to_dict('records')

            # RADICAL OPTIMIZATION 4: Ultra-fast bulk insert
            # Note: Cannot use bypass_document_validation with w=0
            if documents:
                try:
                    result = variants_coll.insert_many(
                        documents,
                        ordered=False
                    )
                    total_rows += len(result.inserted_ids)
                except BulkWriteError as e:
                    total_rows += e.details['nInserted']

            # Log every 5 chunks (less logging = faster)
            if chunk_num % 5 == 0:
                logger.info(f"✓ Loaded {total_rows:,} variants ({chunk_num} chunks processed)")

        logger.info(f"✓ COMPLETE! Loaded {total_rows:,} variants successfully")

    @log_execution_time
    def load_genes(self, csv_path: Optional[str] = None):
        """Load genes from CSV to MongoDB

        Args:
            csv_path: Path to genes CSV file
        """
        if csv_path is None:
            csv_path = self.genes_csv

        logger.info(f"Loading genes from {csv_path}")

        db = self._get_database()
        genes_coll = db['genes']

        # Try to read CSV, handle empty file
        try:
            genes_df = pd.read_csv(csv_path)
        except pd.errors.EmptyDataError:
            logger.warning("Genes CSV file is empty (no gene data in variants)")
            logger.info("Skipping gene loading - 0 genes to load")
            return

        # Check if dataframe is empty
        if len(genes_df) == 0:
            logger.info("No genes to load (0 rows in CSV)")
            return

        # OPTIMIZED: Convert to documents using to_dict('records')
        genes_df = genes_df.where(pd.notna(genes_df), None)
        documents = genes_df.to_dict('records')

        # Bulk insert
        if documents:
            try:
                result = genes_coll.insert_many(documents, ordered=False)
                logger.info(f"Loaded {len(result.inserted_ids)} genes successfully")
            except BulkWriteError as e:
                inserted = e.details['nInserted']
                logger.info(f"Loaded {inserted} genes successfully (some duplicates skipped)")

    @log_execution_time
    def load_drug_annotations(self, csv_path: Optional[str] = None):
        """Load drug annotations from CSV to MongoDB

        Args:
            csv_path: Path to drug annotations CSV file
        """
        if csv_path is None:
            csv_path = self.drug_annotations_csv

        if csv_path is None or not pd.io.common.file_exists(csv_path):
            logger.warning("Drug annotations file not found, skipping")
            return

        logger.info(f"Loading drug annotations from {csv_path}")

        db = self._get_database()
        drug_coll = db['drug_annotations']

        # Try to read CSV, handle empty file
        try:
            drug_df = pd.read_csv(csv_path)
        except pd.errors.EmptyDataError:
            logger.warning("Drug annotations CSV file is empty")
            logger.info("Skipping drug annotations loading - 0 rows to load")
            return

        # Check if dataframe is empty
        if len(drug_df) == 0:
            logger.info("No drug annotations to load (0 rows in CSV)")
            return

        # OPTIMIZED: Convert to documents using to_dict('records')
        drug_df = drug_df.where(pd.notna(drug_df), None)
        documents = drug_df.to_dict('records')

        # Bulk insert
        if documents:
            try:
                result = drug_coll.insert_many(documents, ordered=False)
                logger.info(f"Loaded {len(result.inserted_ids)} drug annotations successfully")
            except BulkWriteError as e:
                inserted = e.details['nInserted']
                logger.info(f"Loaded {inserted} drug annotations successfully")

    @log_execution_time
    def create_mutation_summary(self):
        """Create mutation summary collection using MongoDB aggregation"""
        logger.info("Creating mutation summary using aggregation")

        db = self._get_database()
        variants_coll = db['variants']
        summary_coll = db['mutation_summary']

        # Clear existing data
        summary_coll.delete_many({})

        # MongoDB aggregation pipeline
        pipeline = [
            # Filter out variants without gene symbol
            {"$match": {"gene_symbol": {"$ne": None, "$exists": True}}},

            # Group by chromosome, gene_symbol, and clinical_significance
            {
                "$group": {
                    "_id": {
                        "chromosome": "$chromosome",
                        "gene_symbol": "$gene_symbol",
                        "clinical_significance": "$clinical_significance"
                    },
                    "variant_count": {"$sum": 1},
                    "avg_allele_frequency": {"$avg": "$allele_frequency"},
                    "pathogenic_count": {
                        "$sum": {
                            "$cond": [
                                {
                                    "$in": ["$clinical_significance", ["Pathogenic", "Likely pathogenic"]]
                                },
                                1,
                                0
                            ]
                        }
                    },
                    "benign_count": {
                        "$sum": {
                            "$cond": [
                                {
                                    "$in": ["$clinical_significance", ["Benign", "Likely benign"]]
                                },
                                1,
                                0
                            ]
                        }
                    },
                    "drug_associated_count": {
                        "$sum": {
                            "$cond": [
                                {"$eq": ["$clinical_significance", "Drug response"]},
                                1,
                                0
                            ]
                        }
                    }
                }
            },

            # Reshape the output
            {
                "$project": {
                    "_id": 0,
                    "chromosome": "$_id.chromosome",
                    "gene_symbol": "$_id.gene_symbol",
                    "clinical_significance": "$_id.clinical_significance",
                    "variant_count": 1,
                    "avg_allele_frequency": 1,
                    "pathogenic_count": 1,
                    "benign_count": 1,
                    "drug_associated_count": 1
                }
            }
        ]

        # Execute aggregation and insert results
        logger.info("Running aggregation pipeline...")
        results = list(variants_coll.aggregate(pipeline, allowDiskUse=True))

        if results:
            summary_coll.insert_many(results)
            logger.info(f"Created mutation summary with {len(results)} documents")
        else:
            logger.warning("No mutation summary data generated")

    @log_execution_time
    def load_all(self, drop_existing: bool = False):
        """Complete loading pipeline

        Args:
            drop_existing: Drop existing collections before loading
        """
        logger.info("Starting MongoDB loading pipeline")

        # Test connection
        if not self.test_connection():
            raise Exception("MongoDB connection failed")

        # Create database and collections
        self.create_database()
        self.create_collections(drop_existing=drop_existing)

        # Load data
        self.load_variants()
        self.load_genes()
        self.load_drug_annotations()

        # Create indexes AFTER loading data for better performance
        self.create_indexes()

        # Create summary
        self.create_mutation_summary()

        logger.info("MongoDB loading pipeline completed successfully")

    def get_collection_counts(self) -> dict:
        """Get document counts for all collections

        Returns:
            Dictionary with collection names and document counts
        """
        db = self._get_database()

        collections = ['variants', 'genes', 'drug_annotations', 'mutation_summary']
        counts = {}

        for coll_name in collections:
            try:
                count = db[coll_name].count_documents({})
                counts[coll_name] = count
            except Exception as e:
                logger.warning(f"Error counting {coll_name}: {e}")
                counts[coll_name] = 0

        return counts

    # Alias method for backward compatibility
    def get_table_counts(self) -> dict:
        """Alias for get_collection_counts for backward compatibility"""
        return self.get_collection_counts()

    @property
    def db_config_obj(self):
        """Property to provide db_config attribute for backward compatibility"""
        class DBConfigWrapper:
            def __init__(self, loader):
                self.loader = loader

            def test_connection(self):
                return self.loader.test_connection()

        return DBConfigWrapper(self)

    # Alias for backward compatibility
    db_config = property(lambda self: self.db_config_obj)


# Alias for backward compatibility
MySQLLoader = MongoDBLoader


def main():
    """Main execution function"""
    loader = MongoDBLoader()
    loader.load_all(drop_existing=True)

    # Show statistics
    counts = loader.get_collection_counts()
    print("\nCollection counts:")
    for coll, count in counts.items():
        print(f"  {coll}: {count:,}")


if __name__ == "__main__":
    main()


