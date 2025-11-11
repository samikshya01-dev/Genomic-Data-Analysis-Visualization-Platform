"""
File utility functions for compression, decompression, and parsing
"""
import gzip
import shutil
import os
from typing import Optional, Iterator
import requests
from tqdm import tqdm
import yaml
from pathlib import Path

from ..utils.logger import get_logger

logger = get_logger(__name__)


def download_file(url: str, output_path: str, chunk_size: int = 8192) -> bool:
    """Download file from URL with progress bar

    Args:
        url: URL to download from
        output_path: Path to save downloaded file
        chunk_size: Size of chunks to download

    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"Downloading file from {url}")

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))

        with open(output_path, 'wb') as f, tqdm(
            desc=os.path.basename(output_path),
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as progress_bar:
            for chunk in response.iter_content(chunk_size=chunk_size):
                size = f.write(chunk)
                progress_bar.update(size)

        logger.info(f"File downloaded successfully to {output_path}")
        return True

    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        return False


def decompress_gzip(input_path: str, output_path: Optional[str] = None) -> str:
    """Decompress gzip file

    Args:
        input_path: Path to gzipped file
        output_path: Path to save decompressed file (optional)

    Returns:
        Path to decompressed file
    """
    if output_path is None:
        output_path = input_path.rstrip('.gz')

    try:
        logger.info(f"Decompressing {input_path}")

        file_size = os.path.getsize(input_path)

        with gzip.open(input_path, 'rb') as f_in, open(output_path, 'wb') as f_out, tqdm(
            desc="Decompressing",
            total=file_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as progress_bar:
            while True:
                chunk = f_in.read(8192)
                if not chunk:
                    break
                f_out.write(chunk)
                progress_bar.update(len(chunk))

        logger.info(f"File decompressed to {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Error decompressing file: {e}")
        raise


def compress_gzip(input_path: str, output_path: Optional[str] = None) -> str:
    """Compress file with gzip

    Args:
        input_path: Path to file to compress
        output_path: Path to save compressed file (optional)

    Returns:
        Path to compressed file
    """
    if output_path is None:
        output_path = input_path + '.gz'

    try:
        logger.info(f"Compressing {input_path}")

        with open(input_path, 'rb') as f_in, gzip.open(output_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

        logger.info(f"File compressed to {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Error compressing file: {e}")
        raise


def read_file_in_chunks(file_path: str, chunk_size: int = 10000) -> Iterator[list]:
    """Read file line by line in chunks

    Args:
        file_path: Path to file
        chunk_size: Number of lines per chunk

    Yields:
        List of lines
    """
    try:
        chunk = []

        # Determine if file is gzipped
        is_gzipped = file_path.endswith('.gz')

        open_func = gzip.open if is_gzipped else open
        mode = 'rt' if is_gzipped else 'r'

        with open_func(file_path, mode) as f:
            for line in f:
                chunk.append(line.strip())

                if len(chunk) >= chunk_size:
                    yield chunk
                    chunk = []

            # Yield remaining lines
            if chunk:
                yield chunk

    except Exception as e:
        logger.error(f"Error reading file in chunks: {e}")
        raise


def get_file_size(file_path: str) -> int:
    """Get file size in bytes

    Args:
        file_path: Path to file

    Returns:
        File size in bytes
    """
    return os.path.getsize(file_path)


def get_file_size_readable(file_path: str) -> str:
    """Get human-readable file size

    Args:
        file_path: Path to file

    Returns:
        Human-readable file size
    """
    size = get_file_size(file_path)

    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0

    return f"{size:.2f} PB"


def count_lines(file_path: str) -> int:
    """Count number of lines in file

    Args:
        file_path: Path to file

    Returns:
        Number of lines
    """
    try:
        is_gzipped = file_path.endswith('.gz')
        open_func = gzip.open if is_gzipped else open
        mode = 'rt' if is_gzipped else 'r'

        with open_func(file_path, mode) as f:
            count = sum(1 for _ in f)

        return count

    except Exception as e:
        logger.error(f"Error counting lines: {e}")
        raise


def ensure_directory(directory: str):
    """Ensure directory exists, create if not

    Args:
        directory: Directory path
    """
    os.makedirs(directory, exist_ok=True)


def load_config(config_path: str) -> dict:
    """Load YAML configuration file

    Args:
        config_path: Path to configuration file

    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        raise


def file_exists(file_path: str) -> bool:
    """Check if file exists

    Args:
        file_path: Path to file

    Returns:
        True if file exists, False otherwise
    """
    return os.path.isfile(file_path)


def create_backup(file_path: str) -> str:
    """Create backup of file

    Args:
        file_path: Path to file to backup

    Returns:
        Path to backup file
    """
    from datetime import datetime

    backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    logger.info(f"Backup created: {backup_path}")

    return backup_path

