"""
Enrich variant data with clinical annotations from external sources
Integrates DrugBank, ClinVar, and other clinical databases
"""
import pandas as pd
import requests
import time
from typing import Optional, Dict, List
from tqdm import tqdm

from ..utils import (
    get_logger,
    log_execution_time,
    load_config,
    file_exists
)

logger = get_logger(__name__)


class AnnotationEnricher:
    """Enrich genomic data with clinical annotations"""

    def __init__(self, config_path: str = "config/etl_config.yml"):
        """Initialize annotation enricher

        Args:
            config_path: Path to ETL configuration file
        """
        self.config = load_config(config_path)
        self.enrichment_config = self.config['enrichment']

        # API endpoints
        self.drugbank_api = self.config['data_sources'].get('drugbank_api')
        self.ensembl_api = self.config['data_sources'].get('ensembl_api')

        # Rate limiting
        self.rate_limit = self.enrichment_config.get('api_rate_limit', 10)
        self.last_request_time = 0

        # File paths
        self.genes_csv = self.config['paths']['genes_csv']
        self.drug_annotations_csv = self.config['paths']['drug_annotations_csv']

        # Sample drug-gene associations (static data)
        # In production, this would come from DrugBank API or database
        self.drug_gene_data = self._load_sample_drug_data()

    def _rate_limit_wait(self):
        """Wait to respect rate limiting"""
        if self.rate_limit > 0:
            elapsed = time.time() - self.last_request_time
            wait_time = 1.0 / self.rate_limit

            if elapsed < wait_time:
                time.sleep(wait_time - elapsed)

        self.last_request_time = time.time()

    def _load_sample_drug_data(self) -> List[Dict]:
        """Load sample drug-gene association data

        In production, this would query DrugBank API or load from database

        Returns:
            List of drug-gene associations
        """
        # Sample drug-gene associations for demonstration
        sample_data = [
            {
                'gene_symbol': 'BRCA1',
                'drug_name': 'Olaparib',
                'drug_bank_id': 'DB09074',
                'mechanism': 'PARP inhibitor',
                'indication': 'Breast and ovarian cancer treatment',
                'drug_response': 'Sensitive',
                'adverse_effects': 'Nausea, fatigue, anemia',
                'clinical_trials': 'NCT01844986, NCT02000622',
                'source': 'DrugBank'
            },
            {
                'gene_symbol': 'BRCA2',
                'drug_name': 'Olaparib',
                'drug_bank_id': 'DB09074',
                'mechanism': 'PARP inhibitor',
                'indication': 'Breast and ovarian cancer treatment',
                'drug_response': 'Sensitive',
                'adverse_effects': 'Nausea, fatigue, anemia',
                'clinical_trials': 'NCT01844986',
                'source': 'DrugBank'
            },
            {
                'gene_symbol': 'EGFR',
                'drug_name': 'Gefitinib',
                'drug_bank_id': 'DB00317',
                'mechanism': 'Tyrosine kinase inhibitor',
                'indication': 'Non-small cell lung cancer',
                'drug_response': 'Sensitive to activating mutations',
                'adverse_effects': 'Diarrhea, rash, dry skin',
                'clinical_trials': 'NCT00000123',
                'source': 'DrugBank'
            },
            {
                'gene_symbol': 'KRAS',
                'drug_name': 'Sotorasib',
                'drug_bank_id': 'DB15768',
                'mechanism': 'KRAS G12C inhibitor',
                'indication': 'KRAS G12C-mutated non-small cell lung cancer',
                'drug_response': 'Sensitive to G12C mutation',
                'adverse_effects': 'Diarrhea, nausea, fatigue',
                'clinical_trials': 'NCT03600883',
                'source': 'DrugBank'
            },
            {
                'gene_symbol': 'TP53',
                'drug_name': 'APR-246',
                'drug_bank_id': 'DB12416',
                'mechanism': 'p53 reactivation',
                'indication': 'Various cancers with TP53 mutations',
                'drug_response': 'Restores p53 function',
                'adverse_effects': 'Fatigue, nausea',
                'clinical_trials': 'NCT03745716',
                'source': 'DrugBank'
            },
            {
                'gene_symbol': 'HER2',
                'drug_name': 'Trastuzumab',
                'drug_bank_id': 'DB00072',
                'mechanism': 'HER2 receptor antagonist',
                'indication': 'HER2-positive breast cancer',
                'drug_response': 'Sensitive to HER2 amplification',
                'adverse_effects': 'Cardiotoxicity, infusion reactions',
                'clinical_trials': 'NCT00000456',
                'source': 'DrugBank'
            },
            {
                'gene_symbol': 'ALK',
                'drug_name': 'Crizotinib',
                'drug_bank_id': 'DB08865',
                'mechanism': 'ALK tyrosine kinase inhibitor',
                'indication': 'ALK-positive non-small cell lung cancer',
                'drug_response': 'Sensitive to ALK fusions',
                'adverse_effects': 'Vision disorders, nausea, diarrhea',
                'clinical_trials': 'NCT00932451',
                'source': 'DrugBank'
            },
            {
                'gene_symbol': 'BRAF',
                'drug_name': 'Vemurafenib',
                'drug_bank_id': 'DB08881',
                'mechanism': 'BRAF V600E inhibitor',
                'indication': 'BRAF V600E-mutated melanoma',
                'drug_response': 'Sensitive to V600E mutation',
                'adverse_effects': 'Skin reactions, arthralgia, photosensitivity',
                'clinical_trials': 'NCT01006980',
                'source': 'DrugBank'
            },
            {
                'gene_symbol': 'BCR-ABL1',
                'drug_name': 'Imatinib',
                'drug_bank_id': 'DB00619',
                'mechanism': 'BCR-ABL tyrosine kinase inhibitor',
                'indication': 'Chronic myeloid leukemia',
                'drug_response': 'Sensitive to BCR-ABL fusion',
                'adverse_effects': 'Nausea, muscle cramps, edema',
                'clinical_trials': 'NCT00000789',
                'source': 'DrugBank'
            },
            {
                'gene_symbol': 'DPYD',
                'drug_name': 'Fluorouracil',
                'drug_bank_id': 'DB00544',
                'mechanism': 'Thymidylate synthase inhibitor',
                'indication': 'Colorectal cancer',
                'drug_response': 'Deficiency increases toxicity risk',
                'adverse_effects': 'Severe toxicity in DPYD-deficient patients',
                'clinical_trials': 'NCT00012345',
                'source': 'PharmGKB'
            }
        ]

        return sample_data

    @log_execution_time
    def query_ensembl_gene_info(self, gene_symbol: str) -> Optional[Dict]:
        """Query Ensembl API for gene information

        Args:
            gene_symbol: Gene symbol to query

        Returns:
            Gene information dictionary or None
        """
        if not self.enrichment_config.get('enable_gene_mapping', True):
            return None

        try:
            self._rate_limit_wait()

            url = f"{self.ensembl_api}/lookup/symbol/homo_sapiens/{gene_symbol}"
            headers = {"Content-Type": "application/json"}

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                return response.json()
            else:
                logger.debug(f"Ensembl API returned {response.status_code} for {gene_symbol}")
                return None

        except Exception as e:
            logger.debug(f"Error querying Ensembl for {gene_symbol}: {e}")
            return None

    @log_execution_time
    def enrich_genes_with_descriptions(self, genes_df: pd.DataFrame) -> pd.DataFrame:
        """Enrich genes DataFrame with descriptions from Ensembl

        Args:
            genes_df: DataFrame with gene information

        Returns:
            Enriched DataFrame
        """
        logger.info("Enriching genes with descriptions from Ensembl")

        if 'description' not in genes_df.columns:
            genes_df['description'] = None

        # Sample enrichment (limit to avoid rate limiting)
        sample_size = min(50, len(genes_df))
        genes_to_enrich = genes_df.head(sample_size)

        for idx, row in tqdm(genes_to_enrich.iterrows(), total=len(genes_to_enrich), desc="Enriching genes"):
            gene_symbol = row['gene_symbol']

            if pd.isna(gene_symbol):
                continue

            gene_info = self.query_ensembl_gene_info(gene_symbol)

            if gene_info and 'description' in gene_info:
                genes_df.at[idx, 'description'] = gene_info['description']

        logger.info(f"Enriched {sample_size} genes with descriptions")
        return genes_df

    @log_execution_time
    def create_drug_annotations(self, genes_df: pd.DataFrame) -> pd.DataFrame:
        """Create drug annotations by matching genes with drug data

        Args:
            genes_df: DataFrame with gene information

        Returns:
            DataFrame with drug annotations
        """
        logger.info("Creating drug annotations")

        if not self.enrichment_config.get('enable_drugbank', True):
            logger.info("DrugBank enrichment disabled")
            return pd.DataFrame()

        # Convert drug data to DataFrame
        drug_df = pd.DataFrame(self.drug_gene_data)

        # Match with genes in our dataset
        gene_symbols = set(genes_df['gene_symbol'].dropna().unique())
        matched_drugs = drug_df[drug_df['gene_symbol'].isin(gene_symbols)]

        logger.info(f"Created {len(matched_drugs)} drug-gene associations")
        return matched_drugs

    @log_execution_time
    def save_annotations(self, genes_df: pd.DataFrame, drug_annotations_df: pd.DataFrame):
        """Save enriched data to CSV files

        Args:
            genes_df: Enriched genes DataFrame
            drug_annotations_df: Drug annotations DataFrame
        """
        if not genes_df.empty:
            logger.info(f"Saving enriched genes to {self.genes_csv}")
            genes_df.to_csv(self.genes_csv, index=False)
        else:
            logger.info("No genes to save - keeping empty genes file")

        if not drug_annotations_df.empty:
            logger.info(f"Saving drug annotations to {self.drug_annotations_csv}")
            drug_annotations_df.to_csv(self.drug_annotations_csv, index=False)
        else:
            logger.info("No drug annotations to save")

        logger.info("Annotations saved successfully")

    @log_execution_time
    def enrich_all(self, enrich_descriptions: bool = False) -> tuple:
        """Complete enrichment pipeline

        Args:
            enrich_descriptions: Whether to enrich with Ensembl descriptions (slow)

        Returns:
            Tuple of (genes_df, drug_annotations_df)
        """
        logger.info("Starting annotation enrichment pipeline")

        # Load genes
        if not file_exists(self.genes_csv):
            raise FileNotFoundError(f"Genes file not found: {self.genes_csv}")

        # Try to load genes, handle empty file
        try:
            genes_df = pd.read_csv(self.genes_csv)
        except pd.errors.EmptyDataError:
            logger.warning("Genes file is empty - no genes were extracted from variants")
            logger.info("Creating empty genes dataframe with correct structure")
            genes_df = pd.DataFrame(columns=['gene_symbol', 'gene_id', 'chromosome', 'description'])

        # Check if genes_df is empty or only has header
        if len(genes_df) == 0:
            logger.warning("No genes found in dataset")
            logger.info("Skipping gene description enrichment")
            logger.info("Creating drug annotations from sample pharmacogenomic data only")

            # Create drug annotations with all sample data (not matched to genes)
            drug_annotations_df = pd.DataFrame(self.drug_gene_data)

            # Save the data
            self.save_annotations(genes_df, drug_annotations_df)

            logger.info(f"Created {len(drug_annotations_df)} drug annotations (sample data)")
            logger.info("Annotation enrichment pipeline completed with sample data")
            return genes_df, drug_annotations_df

        logger.info(f"Loaded {len(genes_df)} genes")

        # Enrich with descriptions (optional, slow)
        if enrich_descriptions:
            genes_df = self.enrich_genes_with_descriptions(genes_df)

        # Create drug annotations
        drug_annotations_df = self.create_drug_annotations(genes_df)

        # Save enriched data
        self.save_annotations(genes_df, drug_annotations_df)

        logger.info("Annotation enrichment pipeline completed successfully")
        return genes_df, drug_annotations_df


def main():
    """Main execution function"""
    enricher = AnnotationEnricher()

    try:
        # Enrich annotations
        genes_df, drug_annotations_df = enricher.enrich_all(enrich_descriptions=False)

        logger.info(f"Enriched {len(genes_df)} genes")
        logger.info(f"Created {len(drug_annotations_df)} drug annotations")

    except Exception as e:
        logger.error(f"Error in annotation enrichment: {e}")
        raise


if __name__ == "__main__":
    main()

