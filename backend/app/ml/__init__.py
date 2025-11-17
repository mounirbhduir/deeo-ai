"""
Machine Learning module for DEEO.AI

This module provides ML capabilities for classification and embeddings:
- ZeroShotClassifier: Multi-label classification using BART
- EmbeddingGenerator: Semantic embeddings using Sentence-Transformers
"""

from app.ml.zero_shot_classifier import ZeroShotClassifier
from app.ml.embedding_generator import EmbeddingGenerator

__all__ = [
    "ZeroShotClassifier",
    "EmbeddingGenerator",
]
