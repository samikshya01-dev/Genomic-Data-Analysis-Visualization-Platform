"""
Transform VCF data into structured format
Parse VCF files and normalize variant information
"""
import gzip
import re
import pandas as pd
from typing import Dict, List, Optional, Tuple
from tqdm import tqdm
import vcfpy

from ..utils import (
    get_logger,
    log_execution_time,
    load_config,
    file_exists
)

logger = get_logger(__name__)


class VCFTransformer:
    """Transform VCF data into structured format"""

    def __init__(self, config_path: str = "config/etl_config.yml"):
        """Initialize VCF transformer

        Args:
            config_path: Path to ETL configuration file
        """
        self.config = load_config(config_path)
        self.vcf_file_path = self.config['paths']['vcf_extracted']
        self.vcf_compressed_path = self.config['paths']['vcf_file']
        self.variants_csv = self.config['paths']['variants_csv']
        self.genes_csv = self.config['paths']['genes_csv']
        self.chunk_size = self.config['processing']['chunk_size']

        # VCF parsing configuration
        self.info_fields = self.config['vcf_parser']['extract_info_fields']
        self.clnsig_mapping = self.config['vcf_parser']['clinical_significance_mapping']

    def _parse_info_field(self, info_str: str, field_name: str) -> Optional[str]:
        """Parse specific field from VCF INFO column

        Args:
            info_str: INFO field string
            field_name: Field name to extract

        Returns:
            Field value or None
        """
        pattern = f'{field_name}=([^;]+)'
        match = re.search(pattern, info_str)
        return match.group(1) if match else None

    def _extract_gene_info(self, info_str: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract gene symbol and gene ID from INFO field

        Args:
            info_str: INFO field string

        Returns:
            Tuple of (gene_symbol, gene_id)
        """
        gene_info = self._parse_info_field(info_str, 'GENEINFO')

        if gene_info:
            # Format: GENE_SYMBOL:GENE_ID
            parts = gene_info.split(':')
            if len(parts) >= 2:
                return parts[0], parts[1]
            elif len(parts) == 1:
                return parts[0], None

        return None, None

    def _parse_clinical_significance(self, clnsig_str: Optional[str]) -> str:
        """Parse clinical significance value

        Args:
            clnsig_str: CLNSIG value from INFO field

        Returns:
            Clinical significance description
        """
        if not clnsig_str:
            return "Unknown"

        # Handle multiple values
        if '|' in clnsig_str:
            clnsig_str = clnsig_str.split('|')[0]

        # Try to convert to integer and map
        try:
            clnsig_int = int(clnsig_str)
            return self.clnsig_mapping.get(clnsig_int, "Unknown")
        except (ValueError, KeyError):
            # Return as-is if it's already a string description
            return clnsig_str

    @log_execution_time
    def parse_vcf_simple(self, input_path: Optional[str] = None, max_rows: Optional[int] = None) -> pd.DataFrame:
        """Parse VCF file using simple text parsing with chunked processing (memory-efficient)

        Args:
            input_path: Path to VCF file
            max_rows: Maximum number of rows to parse (None for all)

        Returns:
            DataFrame with parsed variants
        """
        if input_path is None:
            # Try extracted file first, then compressed
            if file_exists(self.vcf_file_path):
                input_path = self.vcf_file_path
            else:
                input_path = self.vcf_compressed_path

        logger.info(f"Parsing VCF file: {input_path}")
        logger.info(f"Using memory-efficient chunked processing (chunk size: {self.chunk_size})")

        # Process in chunks and write directly to CSV to avoid memory issues
        is_gzipped = input_path.endswith('.gz')
        open_func = gzip.open if is_gzipped else open
        mode = 'rt' if is_gzipped else 'r'

        # Temporary file for intermediate results
        temp_variants_csv = self.variants_csv + '.tmp'

        # Clean up any existing temp file to avoid duplicate headers
        import os
        if os.path.exists(temp_variants_csv):
            os.remove(temp_variants_csv)
            logger.info("Removed existing temporary file")

        first_chunk = True
        total_variants = 0
        chunk_buffer = []

        with open_func(input_path, mode) as f:
            # Skip header lines
            for line in f:
                if line.startswith('#CHROM'):
                    break
                elif not line.startswith('#'):
                    break

            # Parse variant lines in chunks
            line_count = 0
            for line in tqdm(f, desc="Parsing VCF"):
                if line.startswith('#'):
                    continue

                parts = line.strip().split('\t')
                if len(parts) < 8:
                    continue

                chrom = parts[0]
                pos = int(parts[1])
                variant_id = parts[2] if parts[2] != '.' else None
                ref = parts[3]
                alt = parts[4]
                qual = parts[5] if parts[5] != '.' else None
                filter_status = parts[6]
                info = parts[7]

                # Extract INFO fields
                af = self._parse_info_field(info, 'AF')
                ac = self._parse_info_field(info, 'AC')
                an = self._parse_info_field(info, 'AN')
                clnsig = self._parse_info_field(info, 'CLNSIG')
                clndn = self._parse_info_field(info, 'CLNDN')

                # Extract gene information
                gene_symbol, gene_id = self._extract_gene_info(info)

                # Parse clinical significance
                clinical_significance = self._parse_clinical_significance(clnsig)

                variant = {
                    'chromosome': chrom,
                    'position': pos,
                    'variant_id': variant_id,
                    'reference_allele': ref,
                    'alternate_allele': alt,
                    'quality': qual,
                    'filter': filter_status,
                    'allele_frequency': float(af) if af else None,
                    'allele_count': int(ac) if ac else None,
                    'total_alleles': int(an) if an else None,
                    'clinical_significance': clinical_significance,
                    'disease_name': clndn,
                    'gene_symbol': gene_symbol,
                    'gene_id': gene_id,
                    'info_raw': info
                }

                chunk_buffer.append(variant)
                line_count += 1

                # Write chunk when buffer is full
                if len(chunk_buffer) >= self.chunk_size:
                    chunk_df = pd.DataFrame(chunk_buffer)
                    chunk_df.to_csv(temp_variants_csv, mode='a', header=first_chunk, index=False)
                    total_variants += len(chunk_buffer)
                    chunk_buffer = []
                    first_chunk = False

                    logger.info(f"Processed {total_variants:,} variants so far...")

                if max_rows and line_count >= max_rows:
                    break

            # Write remaining variants in buffer
            if chunk_buffer:
                chunk_df = pd.DataFrame(chunk_buffer)
                chunk_df.to_csv(temp_variants_csv, mode='a', header=first_chunk, index=False)
                total_variants += len(chunk_buffer)

        logger.info(f"Parsed {total_variants:,} variants using chunked processing")

        # For large datasets, don't load back into memory - just rename the temp file
        # This avoids memory issues with 40M+ variants
        import os
        import shutil

        if total_variants > 1000000:  # For datasets > 1M variants
            logger.info(f"Large dataset detected ({total_variants:,} variants)")
            logger.info("Skipping memory load - using CSV file directly")

            # Move temp file to final location
            if os.path.exists(temp_variants_csv):
                shutil.move(temp_variants_csv, self.variants_csv)
                logger.info(f"Saved variants directly to {self.variants_csv}")

            # Return minimal info - actual data is in CSV file
            # This prevents loading 44M rows into memory
            return pd.DataFrame({
                'note': ['Data saved to CSV - too large to load in memory'],
                'variants_csv': [self.variants_csv],
                'total_variants': [total_variants]
            })
        else:
            # For smaller datasets, load into memory as before
            logger.info("Loading dataset into memory...")
            result_df = pd.read_csv(temp_variants_csv)

            # Clean up temp file
            if os.path.exists(temp_variants_csv):
                os.remove(temp_variants_csv)

            return result_df

    @log_execution_time
    def parse_vcf_with_vcfpy(self, input_path: Optional[str] = None, max_rows: Optional[int] = None) -> pd.DataFrame:
        """Parse VCF file using vcfpy library (more robust)

        Args:
            input_path: Path to VCF file
            max_rows: Maximum number of rows to parse (None for all)

        Returns:
            DataFrame with parsed variants
        """
        if input_path is None:
            if file_exists(self.vcf_file_path):
                input_path = self.vcf_file_path
            else:
                input_path = self.vcf_compressed_path

        logger.info(f"Parsing VCF file with vcfpy: {input_path}")

        variants = []

        try:
            reader = vcfpy.Reader.from_path(input_path)

            for i, record in enumerate(tqdm(reader, desc="Parsing VCF with vcfpy")):
                if max_rows and i >= max_rows:
                    break

                # Extract basic fields
                chrom = record.CHROM
                pos = record.POS
                variant_id = record.ID[0] if record.ID else None
                ref = record.REF
                alt = record.ALT[0].value if record.ALT else None
                qual = record.QUAL
                filter_status = ','.join(record.FILTER) if record.FILTER else 'PASS'

                # Extract INFO fields
                info = record.INFO
                af = info.get('AF', [None])[0] if 'AF' in info else None
                ac = info.get('AC', [None])[0] if 'AC' in info else None
                an = info.get('AN', None) if 'AN' in info else None
                clnsig = info.get('CLNSIG', [None])[0] if 'CLNSIG' in info else None
                clndn = info.get('CLNDN', [None])[0] if 'CLNDN' in info else None
                geneinfo = info.get('GENEINFO', [None])[0] if 'GENEINFO' in info else None

                # Extract gene information
                gene_symbol, gene_id = None, None
                if geneinfo:
                    parts = geneinfo.split(':')
                    if len(parts) >= 2:
                        gene_symbol, gene_id = parts[0], parts[1]
                    elif len(parts) == 1:
                        gene_symbol = parts[0]

                # Parse clinical significance
                clinical_significance = self._parse_clinical_significance(str(clnsig) if clnsig else None)

                variant = {
                    'chromosome': chrom,
                    'position': pos,
                    'variant_id': variant_id,
                    'reference_allele': ref,
                    'alternate_allele': alt,
                    'quality': qual,
                    'filter': filter_status,
                    'allele_frequency': float(af) if af is not None else None,
                    'allele_count': int(ac) if ac is not None else None,
                    'total_alleles': int(an) if an is not None else None,
                    'clinical_significance': clinical_significance,
                    'disease_name': clndn,
                    'gene_symbol': gene_symbol,
                    'gene_id': gene_id
                }

                variants.append(variant)

            reader.close()

        except Exception as e:
            logger.warning(f"vcfpy parsing failed: {e}. Falling back to simple parser.")
            return self.parse_vcf_simple(input_path, max_rows)

        logger.info(f"Parsed {len(variants)} variants")
        return pd.DataFrame(variants)

    @log_execution_time
    def extract_genes(self, variants_df: pd.DataFrame) -> pd.DataFrame:
        """Extract unique genes from variants DataFrame or CSV file

        Args:
            variants_df: DataFrame with variant data (may be placeholder for large datasets)

        Returns:
            DataFrame with unique genes
        """
        logger.info("Extracting unique genes")

        # Check if this is a placeholder for large dataset
        if len(variants_df) < 10 and 'variants_csv' in variants_df.columns:
            # Large dataset - read from CSV in chunks
            csv_path = variants_df['variants_csv'].iloc[0]
            total_variants = variants_df['total_variants'].iloc[0]
            logger.info(f"Large dataset ({total_variants:,} variants) - extracting genes from CSV")

            # Collect unique genes from CSV file in chunks
            unique_genes = set()
            gene_data = {}

            for chunk in pd.read_csv(csv_path, chunksize=100000, usecols=['gene_symbol', 'gene_id', 'chromosome']):
                # Filter out null gene symbols
                chunk_filtered = chunk[chunk['gene_symbol'].notna()]

                # Store gene info
                for _, row in chunk_filtered.iterrows():
                    gene_sym = row['gene_symbol']
                    if gene_sym not in unique_genes:
                        unique_genes.add(gene_sym)
                        gene_data[gene_sym] = {
                            'gene_symbol': gene_sym,
                            'gene_id': row['gene_id'],
                            'chromosome': row['chromosome']
                        }

            genes_df = pd.DataFrame(list(gene_data.values()))
            logger.info(f"Extracted {len(genes_df)} unique genes from large dataset")
            return genes_df
        else:
            # Small dataset - process in memory as before
            genes_df = variants_df[['gene_symbol', 'gene_id', 'chromosome']].copy()
            genes_df = genes_df[genes_df['gene_symbol'].notna()]
            genes_df = genes_df.drop_duplicates(subset=['gene_symbol'])
            genes_df = genes_df.reset_index(drop=True)

            logger.info(f"Extracted {len(genes_df)} unique genes")
            return genes_df

    @log_execution_time
    def save_to_csv(self, variants_df: pd.DataFrame, genes_df: pd.DataFrame):
        """Save DataFrames to CSV files

        Args:
            variants_df: Variants DataFrame (may be placeholder for large datasets)
            genes_df: Genes DataFrame
        """
        # Check if variants are already saved (large dataset case)
        if len(variants_df) < 10 and 'variants_csv' in variants_df.columns:
            csv_path = variants_df['variants_csv'].iloc[0]
            total_variants = variants_df['total_variants'].iloc[0]
            logger.info(f"Variants already saved to {csv_path} ({total_variants:,} rows)")
        else:
            # Normal case - save variants
            logger.info(f"Saving variants to {self.variants_csv}")
            variants_df.to_csv(self.variants_csv, index=False)

        logger.info(f"Saving genes to {self.genes_csv}")
        genes_df.to_csv(self.genes_csv, index=False)

        logger.info("Data saved successfully")

    @log_execution_time
    def transform_all(self, use_vcfpy: bool = False, max_rows: Optional[int] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Complete transformation pipeline

        Args:
            use_vcfpy: Use vcfpy library instead of simple parser
            max_rows: Maximum number of rows to process

        Returns:
            Tuple of (variants_df, genes_df)
        """
        logger.info("Starting VCF transformation pipeline")

        # Parse VCF
        if use_vcfpy:
            variants_df = self.parse_vcf_with_vcfpy(max_rows=max_rows)
        else:
            variants_df = self.parse_vcf_simple(max_rows=max_rows)

        # Extract genes
        genes_df = self.extract_genes(variants_df)

        # Save to CSV
        self.save_to_csv(variants_df, genes_df)

        logger.info("VCF transformation pipeline completed successfully")
        return variants_df, genes_df


def main():
    """Main execution function"""
    transformer = VCFTransformer()

    try:
        # Transform VCF data
        variants_df, genes_df = transformer.transform_all(use_vcfpy=False)

        logger.info(f"Transformed {len(variants_df)} variants")
        logger.info(f"Extracted {len(genes_df)} genes")

    except Exception as e:
        logger.error(f"Error in VCF transformation: {e}")
        raise


if __name__ == "__main__":
    main()

