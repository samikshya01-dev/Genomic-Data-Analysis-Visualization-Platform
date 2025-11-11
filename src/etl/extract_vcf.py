"""
Extract VCF data from Ensembl FTP
Downloads and decompresses VCF files
"""
import os
from typing import Optional

from ..utils import (
    get_logger,
    log_execution_time,
    download_file,
    decompress_gzip,
    load_config,
    file_exists,
    get_file_size_readable
)

logger = get_logger(__name__)


class VCFExtractor:
    """Extract VCF data from remote sources"""

    def __init__(self, config_path: str = "config/etl_config.yml"):
        """Initialize VCF extractor

        Args:
            config_path: Path to ETL configuration file
        """
        self.config = load_config(config_path)
        self.vcf_url = self.config['data_sources']['vcf_url']
        self.raw_data_path = self.config['paths']['raw_data']
        self.vcf_file_path = self.config['paths']['vcf_file']
        self.vcf_extracted_path = self.config['paths']['vcf_extracted']

        # Ensure directories exist
        os.makedirs(self.raw_data_path, exist_ok=True)

    @log_execution_time
    def download_vcf(self, url: Optional[str] = None, force: bool = False) -> str:
        """Download VCF file from URL

        Args:
            url: URL to download from (uses config default if None)
            force: Force re-download even if file exists

        Returns:
            Path to downloaded file
        """
        if url is None:
            url = self.vcf_url

        # Check if file already exists
        if file_exists(self.vcf_file_path) and not force:
            logger.info(f"VCF file already exists at {self.vcf_file_path}")
            logger.info(f"File size: {get_file_size_readable(self.vcf_file_path)}")
            return self.vcf_file_path

        # Download file
        success = download_file(url, self.vcf_file_path)

        if not success:
            raise Exception("Failed to download VCF file")

        logger.info(f"Downloaded file size: {get_file_size_readable(self.vcf_file_path)}")
        return self.vcf_file_path

    @log_execution_time
    def extract_vcf(self, input_path: Optional[str] = None, force: bool = False) -> str:
        """Decompress VCF.gz file

        Args:
            input_path: Path to compressed file (uses config default if None)
            force: Force re-extraction even if file exists

        Returns:
            Path to decompressed file
        """
        if input_path is None:
            input_path = self.vcf_file_path

        # Check if already extracted
        if file_exists(self.vcf_extracted_path) and not force:
            logger.info(f"VCF file already extracted at {self.vcf_extracted_path}")
            logger.info(f"File size: {get_file_size_readable(self.vcf_extracted_path)}")
            return self.vcf_extracted_path

        # Decompress
        output_path = decompress_gzip(input_path, self.vcf_extracted_path)
        logger.info(f"Extracted file size: {get_file_size_readable(output_path)}")

        return output_path

    @log_execution_time
    def extract_all(self, force_download: bool = False, force_extract: bool = False) -> str:
        """Download and extract VCF file (complete extraction pipeline)

        Args:
            force_download: Force re-download
            force_extract: Force re-extraction

        Returns:
            Path to extracted VCF file
        """
        logger.info("Starting VCF extraction pipeline")

        # Download
        downloaded_path = self.download_vcf(force=force_download)

        # Extract
        extracted_path = self.extract_vcf(downloaded_path, force=force_extract)

        logger.info("VCF extraction pipeline completed successfully")
        return extracted_path

    def get_vcf_path(self) -> str:
        """Get path to VCF file (extracted if available, compressed otherwise)

        Returns:
            Path to VCF file
        """
        if file_exists(self.vcf_extracted_path):
            return self.vcf_extracted_path
        elif file_exists(self.vcf_file_path):
            return self.vcf_file_path
        else:
            raise FileNotFoundError("VCF file not found. Please run extract_all() first.")


def main():
    """Main execution function"""
    extractor = VCFExtractor()

    try:
        # Extract VCF data
        vcf_path = extractor.extract_all()
        logger.info(f"VCF file ready at: {vcf_path}")

    except Exception as e:
        logger.error(f"Error in VCF extraction: {e}")
        raise


if __name__ == "__main__":
    main()

