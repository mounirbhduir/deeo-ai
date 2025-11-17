"""
ML Classification Service for AI Research Publications.

This service integrates ZeroShotClassifier with the database to automatically
classify research publications into AI themes.
"""

import logging
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.ml.zero_shot_classifier import ZeroShotClassifier
from app.repositories.theme_repository import ThemeRepository

logger = logging.getLogger(__name__)


# Fallback themes if database is empty
DEFAULT_AI_THEMES = [
    "Natural Language Processing",
    "Computer Vision",
    "Machine Learning",
    "Deep Learning",
    "Reinforcement Learning",
    "Robotics",
    "Neural Networks",
    "Knowledge Representation",
    "Planning and Scheduling",
    "Multi-Agent Systems"
]


class MLClassifierService:
    """
    Service for classifying publications using zero-shot ML.

    This service:
    1. Fetches AI themes from the database
    2. Uses ZeroShotClassifier to classify publication text
    3. Returns top-K themes with confidence scores

    Attributes:
        classifier: ZeroShotClassifier instance
        theme_repository: Repository for accessing themes
        fallback_themes: Default themes if DB is empty
    """

    def __init__(
        self,
        db_session: AsyncSession,
        classifier: Optional[ZeroShotClassifier] = None
    ):
        """
        Initialize MLClassifierService.

        Args:
            db_session: Database session for accessing themes
            classifier: Optional pre-initialized classifier (useful for testing)
        """
        self.classifier = classifier or ZeroShotClassifier.get_instance()
        self.theme_repository = ThemeRepository(db_session)
        self.fallback_themes = DEFAULT_AI_THEMES
        logger.info("MLClassifierService initialized")

    async def get_candidate_labels(self) -> List[str]:
        """
        Get candidate labels (themes) from database.

        Returns:
            List of theme labels to use for classification

        Raises:
            Exception: If fetching themes fails
        """
        try:
            logger.debug("Fetching themes from database")
            themes = await self.theme_repository.list(limit=100)

            if not themes:
                logger.warning(
                    "No themes found in database, using fallback themes"
                )
                return self.fallback_themes

            # Extract labels from themes
            labels = [theme.label for theme in themes if theme.label]
            logger.info(f"Retrieved {len(labels)} themes from database")
            return labels

        except Exception as e:
            logger.error(f"Failed to fetch themes from database: {e}")
            logger.warning("Using fallback themes")
            return self.fallback_themes

    async def classify_publication(
        self,
        title: str,
        abstract: Optional[str] = None,
        top_k: int = 3
    ) -> List[Dict[str, float]]:
        """
        Classify a publication into AI themes.

        Args:
            title: Publication title (required)
            abstract: Publication abstract (optional)
            top_k: Number of top themes to return

        Returns:
            List of dicts with 'label' and 'score' keys
            Example: [{'label': 'NLP', 'score': 0.89}, ...]

        Raises:
            ValueError: If title is empty
            Exception: If classification fails
        """
        # Validation
        if not title or not title.strip():
            logger.error("Empty title provided")
            raise ValueError("Publication title cannot be empty")

        # Combine title and abstract for classification
        if abstract and abstract.strip():
            text = f"{title}. {abstract}"
            logger.debug("Classifying title + abstract")
        else:
            text = title
            logger.debug("Classifying title only (no abstract)")

        # Get candidate labels
        try:
            candidate_labels = await self.get_candidate_labels()

            if not candidate_labels:
                logger.error("No candidate labels available")
                raise Exception("No themes available for classification")

            logger.info(
                f"Classifying publication with {len(candidate_labels)} themes"
            )

            # Classify
            results = self.classifier.classify(
                text=text,
                candidate_labels=candidate_labels,
                top_k=top_k
            )

            logger.info(
                f"Classification complete. "
                f"Top theme: {results[0]['label']} "
                f"(score={results[0]['score']:.3f})"
            )

            return results

        except ValueError as e:
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            raise Exception(f"Failed to classify publication: {e}") from e

    async def classify_batch(
        self,
        publications: List[Dict[str, str]],
        top_k: int = 3
    ) -> List[List[Dict[str, float]]]:
        """
        Classify multiple publications.

        Args:
            publications: List of dicts with 'title' and optionally 'abstract'
            top_k: Number of top themes per publication

        Returns:
            List of classification results (one per publication)

        Raises:
            ValueError: If publications list is empty
            Exception: If classification fails
        """
        if not publications:
            logger.error("Empty publications list")
            raise ValueError("At least one publication is required")

        logger.info(f"Batch classifying {len(publications)} publications")

        results = []
        for i, pub in enumerate(publications):
            try:
                title = pub.get("title", "")
                abstract = pub.get("abstract")

                result = await self.classify_publication(
                    title=title,
                    abstract=abstract,
                    top_k=top_k
                )
                results.append(result)

                logger.debug(f"Classified publication {i+1}/{len(publications)}")

            except Exception as e:
                logger.error(
                    f"Failed to classify publication {i+1}: {e}"
                )
                # Add empty result or re-raise
                results.append([])

        logger.info(f"Batch classification complete: {len(results)} results")
        return results

    async def get_theme_by_label(self, label: str):
        """
        Get theme entity by label.

        Args:
            label: Theme label

        Returns:
            Theme entity or None

        Raises:
            Exception: If database query fails
        """
        try:
            theme = await self.theme_repository.get_by_nom(label)
            return theme
        except Exception as e:
            logger.error(f"Failed to fetch theme '{label}': {e}")
            raise
