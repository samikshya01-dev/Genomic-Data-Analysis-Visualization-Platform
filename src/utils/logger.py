"""
Centralized logging configuration
"""
import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from datetime import datetime
import yaml


class Logger:
    """Centralized logging manager"""

    def __init__(self, config_path: str = "config/etl_config.yml"):
        """Initialize logger

        Args:
            config_path: Path to ETL configuration file
        """
        self.config = self._load_config(config_path)
        self.log_config = self.config.get('logging', {})
        self.log_dir = self.config['paths']['logs']
        self._ensure_log_directory()

    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    def _ensure_log_directory(self):
        """Create log directory if it doesn't exist"""
        os.makedirs(self.log_dir, exist_ok=True)

    def get_logger(self, name: str = None) -> logging.Logger:
        """Get configured logger instance

        Args:
            name: Logger name (usually module name)

        Returns:
            Configured logger instance
        """
        if name is None:
            name = 'genomic_pipeline'

        logger = logging.getLogger(name)

        # Avoid adding handlers multiple times
        if logger.handlers:
            return logger

        # Set logging level
        level_str = self.log_config.get('level', 'INFO')
        level = getattr(logging, level_str.upper(), logging.INFO)
        logger.setLevel(level)

        # Create formatter
        log_format = self.log_config.get(
            'format',
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        formatter = logging.Formatter(log_format)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler with rotation
        log_file = os.path.join(
            self.log_dir,
            f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        )

        rotation_type = self.log_config.get('file_rotation', 'daily')

        if rotation_type == 'daily':
            file_handler = TimedRotatingFileHandler(
                log_file,
                when='midnight',
                interval=1,
                backupCount=self.log_config.get('backup_count', 7)
            )
        else:
            max_bytes = self.log_config.get('max_log_size_mb', 100) * 1024 * 1024
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=self.log_config.get('backup_count', 7)
            )

        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger

    def log_execution_time(self, logger: logging.Logger):
        """Decorator to log function execution time

        Args:
            logger: Logger instance to use

        Returns:
            Decorator function
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = datetime.now()
                logger.info(f"Starting {func.__name__}")

                try:
                    result = func(*args, **kwargs)
                    end_time = datetime.now()
                    duration = (end_time - start_time).total_seconds()
                    logger.info(f"Completed {func.__name__} in {duration:.2f} seconds")
                    return result
                except Exception as e:
                    end_time = datetime.now()
                    duration = (end_time - start_time).total_seconds()
                    logger.error(f"Error in {func.__name__} after {duration:.2f} seconds: {e}")
                    raise

            return wrapper
        return decorator


# Global logger instance
_logger_manager = None


def get_logger(name: str = None) -> logging.Logger:
    """Get or create global logger instance

    Args:
        name: Logger name (usually module name)

    Returns:
        Configured logger instance
    """
    global _logger_manager
    if _logger_manager is None:
        _logger_manager = Logger()

    return _logger_manager.get_logger(name)


def log_execution_time(func):
    """Decorator to log function execution time"""
    logger = get_logger(func.__module__)

    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        logger.info(f"Starting {func.__name__}")

        try:
            result = func(*args, **kwargs)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.info(f"Completed {func.__name__} in {duration:.2f} seconds")
            return result
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.error(f"Error in {func.__name__} after {duration:.2f} seconds: {e}")
            raise

    return wrapper

