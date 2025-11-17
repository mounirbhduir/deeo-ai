"""
Embedding Generation using Sentence Transformers.

This module provides semantic embeddings for text using pre-trained models
from the sentence-transformers library.
"""

import logging
from typing import List, Union, Optional
import numpy as np
from threading import Lock

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """
    Generate semantic embeddings using Sentence Transformers.

    This class uses sentence-transformers to create dense vector embeddings
    for text. These embeddings capture semantic meaning and can be used for
    similarity search, clustering, and classification tasks.

    Attributes:
        model_name: Name of the sentence-transformers model
        model: The loaded SentenceTransformer model
        embedding_dim: Dimension of the embeddings
        _lock: Thread lock for model initialization
    """

    _instance: Optional["EmbeddingGenerator"] = None
    _lock: Lock = Lock()

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the EmbeddingGenerator.

        Args:
            model_name: HuggingFace model name for embeddings
                       Default is all-MiniLM-L6-v2 (384 dimensions, fast)

        Raises:
            ImportError: If sentence-transformers is not installed
        """
        self.model_name = model_name
        self.model = None
        self.embedding_dim = None
        logger.info(f"EmbeddingGenerator initialized with model: {model_name}")

    def _load_model(self) -> None:
        """
        Load the sentence-transformers model (lazy loading).

        Raises:
            ImportError: If sentence-transformers is not installed
            Exception: If model loading fails
        """
        if self.model is not None:
            return

        with self._lock:
            # Double-check after acquiring lock
            if self.model is not None:
                return

            try:
                logger.info(f"Loading embedding model: {self.model_name}")
                from sentence_transformers import SentenceTransformer

                self.model = SentenceTransformer(self.model_name)

                # Get embedding dimension
                test_embedding = self.model.encode(["test"])
                self.embedding_dim = len(test_embedding[0])

                logger.info(
                    f"Model loaded successfully. "
                    f"Embedding dimension: {self.embedding_dim}"
                )

            except ImportError as e:
                logger.error("sentence-transformers library not installed")
                raise ImportError(
                    "sentence-transformers library is required. "
                    "Install with: pip install sentence-transformers"
                ) from e
            except Exception as e:
                logger.error(f"Failed to load model {self.model_name}: {e}")
                raise Exception(f"Model loading failed: {e}") from e

    def encode(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 32,
        normalize: bool = True,
        show_progress: bool = False
    ) -> np.ndarray:
        """
        Generate embeddings for text(s).

        Args:
            texts: Single text string or list of texts
            batch_size: Batch size for processing multiple texts
            normalize: If True, normalize embeddings to unit length
            show_progress: If True, show progress bar for large batches

        Returns:
            numpy array of shape (n_texts, embedding_dim)

        Raises:
            ValueError: If texts is empty
            Exception: If encoding fails

        Examples:
            >>> generator = EmbeddingGenerator()
            >>> embedding = generator.encode("Neural networks")
            >>> print(embedding.shape)
            (1, 384)

            >>> embeddings = generator.encode(["Text 1", "Text 2"])
            >>> print(embeddings.shape)
            (2, 384)
        """
        # Handle single text
        if isinstance(texts, str):
            texts = [texts]

        # Validation
        if not texts:
            logger.warning("Empty text list provided")
            raise ValueError("At least one text is required")

        # Check for empty strings
        if any(not text or not text.strip() for text in texts):
            logger.warning("Empty or whitespace-only text detected")
            raise ValueError("Texts cannot be empty or whitespace-only")

        # Load model if not already loaded
        self._load_model()

        try:
            logger.debug(f"Encoding {len(texts)} text(s)")

            # Generate embeddings
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                normalize_embeddings=normalize,
                show_progress_bar=show_progress,
                convert_to_numpy=True
            )

            logger.debug(
                f"Encoding complete. "
                f"Output shape: {embeddings.shape}"
            )

            return embeddings

        except Exception as e:
            logger.error(f"Encoding failed: {e}")
            raise Exception(f"Embedding generation error: {e}") from e

    def encode_single(
        self,
        text: str,
        normalize: bool = True
    ) -> np.ndarray:
        """
        Generate embedding for a single text (convenience method).

        Args:
            text: Text to encode
            normalize: If True, normalize embedding to unit length

        Returns:
            1D numpy array of shape (embedding_dim,)

        Raises:
            ValueError: If text is empty
            Exception: If encoding fails
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        embeddings = self.encode([text], normalize=normalize)
        return embeddings[0]

    def get_embedding_dimension(self) -> int:
        """
        Get the embedding dimension of the model.

        Returns:
            Embedding dimension (e.g., 384 for all-MiniLM-L6-v2)

        Raises:
            Exception: If model is not loaded
        """
        if self.embedding_dim is None:
            # Load model to get dimension
            self._load_model()

        return self.embedding_dim

    @classmethod
    def get_instance(
        cls,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    ) -> "EmbeddingGenerator":
        """
        Get singleton instance of EmbeddingGenerator.

        This ensures only one model is loaded in memory.

        Args:
            model_name: HuggingFace model name

        Returns:
            Singleton instance of EmbeddingGenerator
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(model_name)
        return cls._instance
