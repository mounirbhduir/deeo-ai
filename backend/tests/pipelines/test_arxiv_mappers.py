"""Tests for ArXiv mappers."""

import pytest
from datetime import datetime

from app.pipelines.arxiv_mappers import (
    ArxivToPublicationMapper,
    ArxivToAuteurMapper,
    ArxivCategoryMapper,
)


class TestArxivToPublicationMapper:
    """Test suite for ArxivToPublicationMapper."""

    def test_map_complete_paper(self):
        """Test mapping with complete paper data."""
        paper = {
            'id': '2311.12345',
            'title': 'Attention is All You Need',
            'summary': 'We propose a new architecture based on attention.',
            'published': '2023-11-20T00:00:00Z',
            'doi': '10.48550/arXiv.2311.12345',
        }

        result = ArxivToPublicationMapper.map(paper)

        assert result['titre'] == 'Attention is All You Need'
        assert result['abstract'] == 'We propose a new architecture based on attention.'
        assert result['arxiv_id'] == '2311.12345'
        assert result['doi'] == '10.48550/arXiv.2311.12345'
        assert result['type_publication'] == 'preprint'
        assert result['source_nom'] == 'arXiv'
        assert result['status'] == 'pending_enrichment'
        assert result['nombre_citations'] == 0
        assert isinstance(result['date_publication'], datetime)

    def test_map_without_doi(self):
        """Test mapping generates DOI if missing."""
        paper = {
            'id': '2311.12345',
            'title': 'Test Paper',
            'summary': 'Abstract',
            'published': '2023-11-20T00:00:00Z',
        }

        result = ArxivToPublicationMapper.map(paper)

        assert result['doi'] == '10.48550/arXiv.2311.12345'

    def test_map_with_url(self):
        """Test mapping generates arXiv URL."""
        paper = {
            'id': '2311.12345',
            'title': 'Test Paper',
            'summary': 'Abstract',
        }

        result = ArxivToPublicationMapper.map(paper)

        assert result['url'] == 'https://arxiv.org/abs/2311.12345'

    def test_map_strips_whitespace(self):
        """Test mapping strips whitespace from title and abstract."""
        paper = {
            'id': '2311.12345',
            'title': '  Test Paper  ',
            'summary': '  Abstract with spaces  ',
        }

        result = ArxivToPublicationMapper.map(paper)

        assert result['titre'] == 'Test Paper'
        assert result['abstract'] == 'Abstract with spaces'

    def test_map_invalid_date(self):
        """Test mapping handles invalid date gracefully."""
        paper = {
            'id': '2311.12345',
            'title': 'Test Paper',
            'summary': 'Abstract',
            'published': 'invalid-date',
        }

        result = ArxivToPublicationMapper.map(paper)

        assert result['date_publication'] is None


class TestArxivToAuteurMapper:
    """Test suite for ArxivToAuteurMapper."""

    def test_map_full_name(self):
        """Test mapping full name."""
        author = {'name': 'John David Smith'}

        result = ArxivToAuteurMapper.map(author)

        assert result['prenom'] == 'John David'
        assert result['nom'] == 'Smith'
        assert result['email'] is None
        assert result['h_index'] is None
        assert result['homepage_url'] is None

    def test_map_single_name(self):
        """Test mapping single name."""
        author = {'name': 'Smith'}

        result = ArxivToAuteurMapper.map(author)

        assert result['prenom'] == ''
        assert result['nom'] == 'Smith'

    def test_map_two_part_name(self):
        """Test mapping two-part name."""
        author = {'name': 'John Smith'}

        result = ArxivToAuteurMapper.map(author)

        assert result['prenom'] == 'John'
        assert result['nom'] == 'Smith'

    def test_map_empty_name(self):
        """Test mapping empty name."""
        author = {'name': ''}

        result = ArxivToAuteurMapper.map(author)

        assert result['prenom'] == ''
        assert result['nom'] == ''

    def test_parse_name(self):
        """Test name parsing."""
        assert ArxivToAuteurMapper._parse_name('John Smith') == ('John', 'Smith')
        assert ArxivToAuteurMapper._parse_name('John David Smith') == ('John David', 'Smith')
        assert ArxivToAuteurMapper._parse_name('Smith') == ('', 'Smith')
        assert ArxivToAuteurMapper._parse_name('') == ('', '')

    def test_map_authors_multiple(self):
        """Test mapping multiple authors."""
        authors = [
            {'name': 'John Smith'},
            {'name': 'Jane Doe'},
            {'name': 'Bob Johnson'},
        ]

        results = ArxivToAuteurMapper.map_authors(authors)

        assert len(results) == 3
        assert results[0]['nom'] == 'Smith'
        assert results[1]['nom'] == 'Doe'
        assert results[2]['nom'] == 'Johnson'

    def test_map_authors_filters_empty_names(self):
        """Test mapping filters authors without names."""
        authors = [
            {'name': 'John Smith'},
            {'name': ''},
            {'other_field': 'value'},
        ]

        results = ArxivToAuteurMapper.map_authors(authors)

        assert len(results) == 1
        assert results[0]['nom'] == 'Smith'


class TestArxivCategoryMapper:
    """Test suite for ArxivCategoryMapper."""

    def test_map_categories(self):
        """Test mapping arXiv categories to themes."""
        categories = ['cs.AI', 'cs.LG', 'cs.CV']

        themes = ArxivCategoryMapper.map_categories(categories)

        assert 'Artificial Intelligence' in themes
        assert 'Machine Learning' in themes
        assert 'Computer Vision' in themes

    def test_map_categories_removes_duplicates(self):
        """Test mapping removes duplicate themes."""
        categories = ['cs.LG', 'stat.ML', 'cs.LG']

        themes = ArxivCategoryMapper.map_categories(categories)

        assert themes.count('Machine Learning') == 1

    def test_map_categories_unknown(self):
        """Test mapping ignores unknown categories."""
        categories = ['cs.LG', 'unknown.CAT', 'cs.AI']

        themes = ArxivCategoryMapper.map_categories(categories)

        assert len(themes) == 2
        assert 'Machine Learning' in themes
        assert 'Artificial Intelligence' in themes

    def test_get_primary_theme(self):
        """Test getting primary theme."""
        categories = ['cs.CV', 'cs.AI']

        primary = ArxivCategoryMapper.get_primary_theme(categories)

        assert primary == 'Computer Vision'

    def test_get_primary_theme_none(self):
        """Test getting primary theme returns None for unknown categories."""
        categories = ['unknown.CAT']

        primary = ArxivCategoryMapper.get_primary_theme(categories)

        assert primary is None

    def test_extract_themes_from_text(self):
        """Test extracting themes from text."""
        text = 'Deep learning for computer vision and image recognition'

        themes = ArxivCategoryMapper.extract_themes_from_text(text)

        assert 'Neural Networks' in themes
        assert 'Computer Vision' in themes

    def test_extract_themes_no_match(self):
        """Test extracting themes with no matches."""
        text = 'Some random content without any matching keywords'

        themes = ArxivCategoryMapper.extract_themes_from_text(text)

        assert len(themes) == 0
