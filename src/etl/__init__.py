"""
ETL module initialization
"""
from .extract_vcf import VCFExtractor
from .transform_vcf import VCFTransformer
from .load_to_mysql import MongoDBLoader, MySQLLoader  # MySQLLoader is alias for MongoDBLoader
from .enrich_annotations import AnnotationEnricher

__all__ = [
    'VCFExtractor',
    'VCFTransformer',
    'MongoDBLoader',
    'MySQLLoader',  # Backward compatibility
    'AnnotationEnricher',
]

