"""
Database configuration and connection management
NOTE: This module is for MySQL (legacy). MongoDB is now used via load_to_mysql.py
"""
import yaml
import os
from typing import Optional
import logging

# Optional MySQL imports - only needed if using MySQL backend
try:
    from sqlalchemy import create_engine, event
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import QueuePool
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("MySQL libraries not available. Only MongoDB backend is supported.")

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Manages database configuration and connections"""

    def __init__(self, config_path: str = "config/db_config.yml"):
        """Initialize database configuration

        Args:
            config_path: Path to database configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.engine = None
        self.Session = None

    def _load_config(self) -> dict:
        """Load database configuration from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Database configuration loaded from {self.config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML configuration: {e}")
            raise

    def get_connection_string(self) -> str:
        """Generate SQLAlchemy connection string"""
        db_config = self.config['database']
        conn_str = self.config['connection_string'].format(**db_config)
        return conn_str

    def get_engine(self):
        """Create and return SQLAlchemy engine"""
        if self.engine is None:
            conn_str = self.get_connection_string()
            perf_config = self.config['database']

            self.engine = create_engine(
                conn_str,
                poolclass=QueuePool,
                pool_size=perf_config.get('pool_size', 10),
                max_overflow=perf_config.get('max_overflow', 20),
                pool_timeout=perf_config.get('pool_timeout', 30),
                pool_recycle=perf_config.get('pool_recycle', 3600),
                echo=False
            )

            # Add event listener for connection checkout
            @event.listens_for(self.engine, "connect")
            def receive_connect(dbapi_conn, connection_record):
                connection_record.info['pid'] = os.getpid()

            logger.info("Database engine created successfully")

        return self.engine

    def get_session(self):
        """Create and return SQLAlchemy session"""
        if self.Session is None:
            engine = self.get_engine()
            self.Session = sessionmaker(bind=engine)

        return self.Session()

    def get_raw_connection(self):
        """Get raw MySQL connection using mysql-connector"""
        db_config = self.config['database']

        try:
            connection = mysql.connector.connect(
                host=db_config['host'],
                port=db_config['port'],
                database=db_config['database'],
                user=db_config['user'],
                password=db_config['password'],
                charset=db_config['charset']
            )
            logger.info("Raw MySQL connection established")
            return connection
        except mysql.connector.Error as e:
            logger.error(f"Error connecting to MySQL: {e}")
            raise

    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            conn = self.get_raw_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            conn.close()

            if result[0] == 1:
                logger.info("Database connection test successful")
                return True
            return False
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False

    def create_database_if_not_exists(self):
        """Create database if it doesn't exist"""
        db_config = self.config['database']

        try:
            # Connect without specifying database
            connection = mysql.connector.connect(
                host=db_config['host'],
                port=db_config['port'],
                user=db_config['user'],
                password=db_config['password']
            )

            cursor = connection.cursor()
            db_name = db_config['database']
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            logger.info(f"Database '{db_name}' created or already exists")

            cursor.close()
            connection.close()

        except mysql.connector.Error as e:
            logger.error(f"Error creating database: {e}")
            raise

    def get_table_name(self, table_key: str) -> str:
        """Get table name from configuration

        Args:
            table_key: Key for table name in config

        Returns:
            Table name
        """
        return self.config['tables'].get(table_key, table_key)

    def get_performance_config(self) -> dict:
        """Get performance configuration"""
        return self.config.get('performance', {})

    def close(self):
        """Close database connections"""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections closed")


# Global database config instance
_db_config: Optional[DatabaseConfig] = None


def get_db_config(config_path: str = "config/db_config.yml") -> DatabaseConfig:
    """Get or create global database configuration instance"""
    global _db_config
    if _db_config is None:
        _db_config = DatabaseConfig(config_path)
    return _db_config

