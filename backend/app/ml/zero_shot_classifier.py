"""
Zero-Shot Classification using BART for multi-label text classification.

This module provides a ZeroShotClassifier that uses facebook/bart-large-mnli
for classifying text into multiple candidate labels without fine-tuning.
"""

import logging
from typing import Dict, List, Optional
from threading import Lock

logger = logging.getLogger(__name__)


class ZeroShotClassifier:
    """
    Zero-shot text classifier using BART model.
    
    This classifier uses facebook/bart-large-mnli for multi-label classification
    without requiring training data. It's ideal for classifying research papers
    into predefined AI themes.
    
    Attributes:
        model_name: Name of the HuggingFace model to use
        pipeline: Transformers pipeline for zero-shot classification
        _lock: Thread lock for model initialization
    """
    
    _instance: Optional["ZeroShotClassifier"] = None
    _lock: Lock = Lock()
    
    def __init__(self, model_name: str = "facebook/bart-large-mnli"):
        """
        Initialize the ZeroShotClassifier.
        
        Args:
            model_name: HuggingFace model name for zero-shot classification
            
        Raises:
            ImportError: If transformers library is not installed
            Exception: If model loading fails
        """
        self.model_name = model_name
        self.pipeline = None
        logger.info(f"ZeroShotClassifier initialized with model: {model_name}")
    
    def _load_model(self) -> None:
        """
        Load the transformers pipeline (lazy loading).
        
        This method loads the model only when needed to avoid
        unnecessary resource consumption during initialization.
        
        Raises:
            ImportError: If transformers is not installed
            Exception: If model loading fails
        """
        if self.pipeline is not None:
            return
            
        with self._lock:
            # Double-check after acquiring lock
            if self.pipeline is not None:
                return
                
            try:
                logger.info(f"Loading zero-shot classification model: {self.model_name}")
                from transformers import pipeline
                
                self.pipeline = pipeline(
                    "zero-shot-classification",
                    model=self.model_name,
                    device=-1  # CPU only for now
                )
                logger.info("Model loaded successfully")
                
            except ImportError as e:
                logger.error("transformers library not installed")
                raise ImportError(
                    "transformers library is required. "
                    "Install with: pip install transformers torch"
                ) from e
            except Exception as e:
                logger.error(f"Failed to load model {self.model_name}: {e}")
                raise Exception(f"Model loading failed: {e}") from e
    
    def classify(
        self,
        text: str,
        candidate_labels: List[str],
        top_k: int = 3,
        multi_label: bool = True
    ) -> List[Dict[str, float]]:
        """
        Classify text into candidate labels.
        
        Args:
            text: Text to classify
            candidate_labels: List of possible labels
            top_k: Number of top labels to return
            multi_label: If True, allows multiple labels (independent probabilities)
            
        Returns:
            List of dicts with 'label' and 'score' keys, sorted by score descending
            
        Raises:
            ValueError: If text is empty or no candidate labels provided
            Exception: If classification fails
            
        Examples:
            >>> classifier = ZeroShotClassifier()
            >>> text = "Neural networks for image recognition"
            >>> labels = ["Computer Vision", "NLP", "Reinforcement Learning"]
            >>> results = classifier.classify(text, labels, top_k=2)
            >>> print(results)
            [{'label': 'Computer Vision', 'score': 0.89}, 
             {'label': 'NLP', 'score': 0.23}]
        """
        # Validation
        if not text or not text.strip():
            logger.warning("Empty text provided for classification")
            raise ValueError("Text cannot be empty")
            
        if not candidate_labels:
            logger.warning("No candidate labels provided")
            raise ValueError("At least one candidate label is required")
            
        # Load model if not already loaded
        self._load_model()
        
        try:
            logger.debug(
                f"Classifying text (length={len(text)}) "
                f"into {len(candidate_labels)} labels"
            )
            
            # Run classification
            result = self.pipeline(
                text,
                candidate_labels=candidate_labels,
                multi_label=multi_label
            )
            
            # Format results
            classifications = [
                {"label": label, "score": float(score)}
                for label, score in zip(result["labels"], result["scores"])
            ]
            
            # Return top-k
            top_classifications = classifications[:top_k]
            
            logger.debug(
                f"Classification complete. Top result: "
                f"{top_classifications[0]['label']} "
                f"(score={top_classifications[0]['score']:.3f})"
            )
            
            return top_classifications
            
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            raise Exception(f"Classification error: {e}") from e
    
    @classmethod
    def get_instance(cls, model_name: str = "facebook/bart-large-mnli") -> "ZeroShotClassifier":
        """
        Get singleton instance of ZeroShotClassifier.
        
        This ensures only one model is loaded in memory.
        
        Args:
            model_name: HuggingFace model name
            
        Returns:
            Singleton instance of ZeroShotClassifier
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(model_name)
        return cls._instance
