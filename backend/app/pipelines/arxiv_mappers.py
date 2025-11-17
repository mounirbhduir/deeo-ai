"""Mappers for transforming arXiv data to database models.

This module provides mappers to convert arXiv API responses into database models:
- ArxivToPublicationMapper: Maps arXiv papers to Publication models
- ArxivToAuteurMapper: Parses author names from arXiv format
- ArxivCategoryMapper: Maps arXiv categories to database themes
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from app.logging import get_logger

logger = get_logger(__name__)


class ArxivToPublicationMapper:
    """Maps arXiv paper data to Publication model format.

    Transforms arXiv API responses into the structure expected by
    the Publication database model.
    """

    @staticmethod
    def map(arxiv_paper: Dict[str, Any]) -> Dict[str, Any]:
        """Map arXiv paper to Publication format.

        Args:
            arxiv_paper: Paper data from arXiv API

        Returns:
            Dictionary matching Publication model schema

        Example:
            >>> paper = {
            ...     'id': '2311.12345',
            ...     'title': 'Attention Survey',
            ...     'summary': 'Abstract...',
            ...     'published': '2023-11-20T00:00:00Z',
            ...     'doi': '10.48550/arXiv.2311.12345'
            ... }
            >>> result = ArxivToPublicationMapper.map(paper)
            >>> result['titre']
            'Attention Survey'
        """
        try:
            # Parse publication date
            date_publication = None
            if arxiv_paper.get('published'):
                try:
                    date_publication = datetime.fromisoformat(
                        arxiv_paper['published'].replace('Z', '+00:00')
                    )
                except ValueError:
                    logger.warning(
                        "arxiv.mapper.date_parse_failed",
                        date_str=arxiv_paper['published'],
                    )

            # Build DOI (use provided or generate from arXiv ID)
            doi = arxiv_paper.get('doi')
            if not doi and arxiv_paper.get('id'):
                doi = f"10.48550/arXiv.{arxiv_paper['id']}"

            # Map to Publication format
            publication = {
                'titre': arxiv_paper.get('title', '').strip(),
                'abstract': arxiv_paper.get('summary', '').strip(),
                'arxiv_id': arxiv_paper.get('id'),
                'doi': doi,
                'date_publication': date_publication,
                'type_publication': 'preprint',
                'source_nom': 'arXiv',
                'status': 'pending_enrichment',
                'url': f"https://arxiv.org/abs/{arxiv_paper['id']}" if arxiv_paper.get('id') else None,
                'nombre_citations': 0,
                'score_pertinence': 0.0,
            }

            logger.debug(
                "arxiv.mapper.publication.mapped",
                arxiv_id=arxiv_paper.get('id'),
                title=publication['titre'][:50],
            )

            return publication

        except Exception as e:
            logger.error(
                "arxiv.mapper.publication.failed",
                error=str(e),
                arxiv_id=arxiv_paper.get('id'),
            )
            raise


class ArxivToAuteurMapper:
    """Maps arXiv author data to Auteur model format.

    Parses author names from arXiv format and extracts first/last names.
    """

    @staticmethod
    def map(author: Dict[str, str]) -> Dict[str, Any]:
        """Map arXiv author to Auteur format.

        Args:
            author: Author data from arXiv (e.g., {'name': 'John Smith'})

        Returns:
            Dictionary matching Auteur model schema

        Example:
            >>> author = {'name': 'John David Smith'}
            >>> result = ArxivToAuteurMapper.map(author)
            >>> result['prenom']
            'John David'
            >>> result['nom']
            'Smith'
        """
        try:
            name = author.get('name', '').strip()
            prenom, nom = ArxivToAuteurMapper._parse_name(name)

            auteur = {
                'nom': nom,
                'prenom': prenom,
                'email': None,
                'affiliations': None,
                'h_index': None,
                'url_profile': None,
            }

            logger.debug(
                "arxiv.mapper.auteur.mapped",
                name=name,
                prenom=prenom,
                nom=nom,
            )

            return auteur

        except Exception as e:
            logger.error(
                "arxiv.mapper.auteur.failed",
                error=str(e),
                author=author,
            )
            raise

    @staticmethod
    def _parse_name(full_name: str) -> tuple[str, str]:
        """Parse full name into first name and last name.

        Assumes last word is the last name, everything else is first name.

        Args:
            full_name: Full name string

        Returns:
            Tuple of (first_name, last_name)

        Example:
            >>> ArxivToAuteurMapper._parse_name('John David Smith')
            ('John David', 'Smith')
            >>> ArxivToAuteurMapper._parse_name('Smith')
            ('', 'Smith')
        """
        if not full_name:
            return '', ''

        parts = full_name.split()
        if len(parts) == 1:
            return '', parts[0]
        else:
            return ' '.join(parts[:-1]), parts[-1]

    @staticmethod
    def map_authors(authors: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Map multiple authors from arXiv format.

        Args:
            authors: List of author dictionaries from arXiv

        Returns:
            List of author dictionaries in Auteur format
        """
        return [
            ArxivToAuteurMapper.map(author)
            for author in authors
            if author.get('name')
        ]


class ArxivCategoryMapper:
    """Maps arXiv categories to database themes.

    Provides mapping between arXiv category codes and human-readable themes.
    """

    # Category to theme mapping
    CATEGORY_MAPPING = {
        'cs.AI': 'Artificial Intelligence',
        'cs.LG': 'Machine Learning',
        'cs.CV': 'Computer Vision',
        'cs.CL': 'Natural Language Processing',
        'cs.NE': 'Neural Networks',
        'stat.ML': 'Statistical Machine Learning',
        'cs.RO': 'Robotics',
        'cs.IR': 'Information Retrieval',
        'cs.HC': 'Human-Computer Interaction',
        'cs.CR': 'Cryptography and Security',
    }

    # Theme to keywords mapping for better categorization
    THEME_KEYWORDS = {
        'Artificial Intelligence': ['ai', 'artificial intelligence', 'intelligent systems'],
        'Machine Learning': ['machine learning', 'ml', 'supervised', 'unsupervised'],
        'Computer Vision': ['vision', 'image', 'visual', 'object detection'],
        'Natural Language Processing': ['nlp', 'language', 'text', 'linguistic'],
        'Neural Networks': ['neural', 'deep learning', 'cnn', 'rnn', 'transformer'],
        'Statistical Machine Learning': ['statistics', 'probabilistic', 'bayesian'],
        'Robotics': ['robot', 'robotics', 'autonomous'],
        'Information Retrieval': ['search', 'retrieval', 'ranking'],
        'Human-Computer Interaction': ['hci', 'interaction', 'user interface'],
        'Cryptography and Security': ['security', 'cryptography', 'privacy'],
    }

    @classmethod
    def map_categories(cls, categories: List[str]) -> List[str]:
        """Map arXiv categories to theme names.

        Args:
            categories: List of arXiv category codes

        Returns:
            List of theme names

        Example:
            >>> ArxivCategoryMapper.map_categories(['cs.AI', 'cs.LG'])
            ['Artificial Intelligence', 'Machine Learning']
        """
        themes = []
        for category in categories:
            theme = cls.CATEGORY_MAPPING.get(category)
            if theme and theme not in themes:
                themes.append(theme)

        logger.debug(
            "arxiv.mapper.categories.mapped",
            categories=categories,
            themes=themes,
        )

        return themes

    @classmethod
    def get_primary_theme(cls, categories: List[str]) -> Optional[str]:
        """Get the primary theme from a list of categories.

        Returns the first mapped theme, or None if no mapping exists.

        Args:
            categories: List of arXiv category codes

        Returns:
            Primary theme name or None

        Example:
            >>> ArxivCategoryMapper.get_primary_theme(['cs.LG', 'stat.ML'])
            'Machine Learning'
        """
        themes = cls.map_categories(categories)
        return themes[0] if themes else None

    @classmethod
    def extract_themes_from_text(cls, text: str) -> List[str]:
        """Extract themes from text based on keywords.

        Useful for categorizing papers when categories are not available.

        Args:
            text: Text to analyze (title, abstract, etc.)

        Returns:
            List of matching theme names

        Example:
            >>> text = 'Deep learning for computer vision'
            >>> ArxivCategoryMapper.extract_themes_from_text(text)
            ['Neural Networks', 'Computer Vision']
        """
        text_lower = text.lower()
        matching_themes = []

        for theme, keywords in cls.THEME_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                if theme not in matching_themes:
                    matching_themes.append(theme)

        logger.debug(
            "arxiv.mapper.themes_extracted",
            text=text[:50],
            themes=matching_themes,
        )

        return matching_themes
