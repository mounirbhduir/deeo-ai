"""
Tests unitaires pour PublicationRepository

Teste les méthodes spécialisées : DOI, arXiv ID, statut, recherche full-text, eager loading.
"""
import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import PublicationRepository
from app.models.enums import StatusPublicationEnum, TypePublicationEnum


@pytest.mark.asyncio
async def test_get_by_doi_existing(
    async_session: AsyncSession,
    publication_data: dict
):
    """Test récupération par DOI existant."""
    # Arrange
    repository = PublicationRepository(async_session)
    created = await repository.create(publication_data)
    
    # Act
    result = await repository.get_by_doi(publication_data["doi"])
    
    # Assert
    assert result is not None
    assert result.id == created.id
    assert result.doi == publication_data["doi"]


@pytest.mark.asyncio
async def test_get_by_doi_nonexistent(async_session: AsyncSession):
    """Test récupération par DOI inexistant."""
    # Arrange
    repository = PublicationRepository(async_session)
    
    # Act
    result = await repository.get_by_doi("10.9999/nonexistent")
    
    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_get_by_arxiv_id_existing(
    async_session: AsyncSession,
    publication_data: dict
):
    """Test récupération par arXiv ID existant."""
    # Arrange
    repository = PublicationRepository(async_session)
    created = await repository.create(publication_data)
    
    # Act
    result = await repository.get_by_arxiv_id(publication_data["arxiv_id"])
    
    # Assert
    assert result is not None
    assert result.id == created.id
    assert result.arxiv_id == publication_data["arxiv_id"]


@pytest.mark.asyncio
async def test_get_by_arxiv_id_nonexistent(async_session: AsyncSession):
    """Test récupération par arXiv ID inexistant."""
    # Arrange
    repository = PublicationRepository(async_session)
    
    # Act
    result = await repository.get_by_arxiv_id("9999.99999")
    
    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_get_by_status(
    async_session: AsyncSession,
    publication_data: dict
):
    """Test récupération par statut d'enrichissement."""
    # Arrange
    repository = PublicationRepository(async_session)
    
    # Créer 3 publications PUBLISHED
    for i in range(3):
        data = publication_data.copy()
        data["doi"] = f"10.1234/test.{i}"
        data["arxiv_id"] = f"2401.{10000+i:05d}"
        data["status"] = StatusPublicationEnum.PUBLISHED
        await repository.create(data)
    
    # Créer 2 publications PENDING_ENRICHMENT
    for i in range(3, 5):
        data = publication_data.copy()
        data["doi"] = f"10.1234/test.{i}"
        data["arxiv_id"] = f"2401.{10000+i:05d}"
        data["status"] = StatusPublicationEnum.PENDING_ENRICHMENT
        await repository.create(data)
    
    # Act
    published = await repository.get_by_status(StatusPublicationEnum.PUBLISHED)
    pending = await repository.get_by_status(StatusPublicationEnum.PENDING_ENRICHMENT)
    
    # Assert
    assert len(published) == 3
    assert len(pending) == 2
    assert all(p.status == StatusPublicationEnum.PUBLISHED for p in published)
    assert all(p.status == StatusPublicationEnum.PENDING_ENRICHMENT for p in pending)


@pytest.mark.asyncio
async def test_search_by_titre(
    async_session: AsyncSession,
    publication_data: dict
):
    """Test recherche full-text sur titre."""
    # Arrange
    repository = PublicationRepository(async_session)
    
    # Créer publications avec différents titres
    titles = [
        "Attention Is All You Need",
        "BERT: Pre-training of Deep Bidirectional Transformers",
        "GPT-3: Language Models are Few-Shot Learners"
    ]
    
    for i, title in enumerate(titles):
        data = publication_data.copy()
        data["titre"] = title
        data["doi"] = f"10.1234/test.{i}"
        data["arxiv_id"] = f"2401.{10000+i:05d}"
        await repository.create(data)
    
    # Act
    results_attention = await repository.search("Attention")
    results_transformers = await repository.search("Transformers")
    results_gpt = await repository.search("GPT")
    
    # Assert
    assert len(results_attention) == 1
    assert "Attention" in results_attention[0].titre
    
    assert len(results_transformers) == 1
    assert "Transformers" in results_transformers[0].titre
    
    assert len(results_gpt) == 1
    assert "GPT" in results_gpt[0].titre


@pytest.mark.asyncio
async def test_search_by_abstract(
    async_session: AsyncSession,
    publication_data: dict
):
    """Test recherche full-text sur résumé."""
    # Arrange
    repository = PublicationRepository(async_session)
    
    data = publication_data.copy()
    data["abstract"] = "This paper introduces Transformers, a novel architecture based on attention mechanisms."
    await repository.create(data)
    
    # Act
    results = await repository.search("architecture")
    
    # Assert
    assert len(results) == 1
    assert "architecture" in results[0].abstract.lower()


@pytest.mark.asyncio
async def test_search_no_results(async_session: AsyncSession):
    """Test recherche sans résultats."""
    # Arrange
    repository = PublicationRepository(async_session)
    
    # Act
    results = await repository.search("nonexistentkeyword123456")
    
    # Assert
    assert results == []


@pytest.mark.asyncio
async def test_get_recent(
    async_session: AsyncSession,
    publication_data: dict
):
    """Test récupération des publications récentes (tri par date DESC)."""
    # Arrange
    repository = PublicationRepository(async_session)
    
    # Créer publications avec différentes dates
    dates = [
        date(2022, 1, 1),
        date(2023, 6, 15),
        date(2024, 11, 10),
        date(2021, 12, 31),
    ]
    
    for i, pub_date in enumerate(dates):
        data = publication_data.copy()
        data["date_publication"] = pub_date
        data["doi"] = f"10.1234/test.{i}"
        data["arxiv_id"] = f"2401.{10000+i:05d}"
        await repository.create(data)
    
    # Act
    recent = await repository.get_recent(limit=10)
    
    # Assert
    assert len(recent) == 4
    # Vérifier tri décroissant
    assert recent[0].date_publication == date(2024, 11, 10)
    assert recent[1].date_publication == date(2023, 6, 15)
    assert recent[2].date_publication == date(2022, 1, 1)
    assert recent[3].date_publication == date(2021, 12, 31)


@pytest.mark.asyncio
async def test_get_recent_with_limit(
    async_session: AsyncSession,
    publication_data: dict
):
    """Test pagination des publications récentes."""
    # Arrange
    repository = PublicationRepository(async_session)
    
    # Créer 5 publications
    for i in range(5):
        data = publication_data.copy()
        data["date_publication"] = date(2024, 1, i + 1)
        data["doi"] = f"10.1234/test.{i}"
        data["arxiv_id"] = f"2401.{10000+i:05d}"
        await repository.create(data)
    
    # Act
    recent = await repository.get_recent(limit=3)
    
    # Assert
    assert len(recent) == 3


@pytest.mark.asyncio
async def test_count_by_status(
    async_session: AsyncSession,
    publication_data: dict
):
    """Test comptage par statut."""
    # Arrange
    repository = PublicationRepository(async_session)
    
    # Créer 3 PUBLISHED
    for i in range(3):
        data = publication_data.copy()
        data["doi"] = f"10.1234/test.{i}"
        data["arxiv_id"] = f"2401.{10000+i:05d}"
        data["status"] = StatusPublicationEnum.PUBLISHED
        await repository.create(data)
    
    # Créer 2 PENDING_ENRICHMENT
    for i in range(3, 5):
        data = publication_data.copy()
        data["doi"] = f"10.1234/test.{i}"
        data["arxiv_id"] = f"2401.{10000+i:05d}"
        data["status"] = StatusPublicationEnum.PENDING_ENRICHMENT
        await repository.create(data)
    
    # Act
    count_published = await repository.count_by_status(StatusPublicationEnum.PUBLISHED)
    count_pending = await repository.count_by_status(StatusPublicationEnum.PENDING_ENRICHMENT)
    count_enriched = await repository.count_by_status(StatusPublicationEnum.ENRICHED)
    
    # Assert
    assert count_published == 3
    assert count_pending == 2
    assert count_enriched == 0


@pytest.mark.asyncio
async def test_get_with_authors(
    async_session: AsyncSession,
    created_publication
):
    """Test eager loading des auteurs."""
    # Arrange
    repository = PublicationRepository(async_session)
    
    # Act
    result = await repository.get_with_authors(created_publication.id)
    
    # Assert
    assert result is not None
    assert result.id == created_publication.id
    # Note: auteurs sera [] car pas créés dans ce test, mais la relation est chargée
    assert hasattr(result, 'auteurs')


@pytest.mark.asyncio
async def test_get_with_authors_nonexistent(async_session: AsyncSession):
    """Test eager loading des auteurs pour publication inexistante."""
    # Arrange
    from uuid import uuid4
    repository = PublicationRepository(async_session)
    fake_id = uuid4()
    
    # Act
    result = await repository.get_with_authors(fake_id)
    
    # Assert
    assert result is None
