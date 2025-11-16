"""
Tests unitaires pour OrganisationRepository

Teste les méthodes spécialisées : nom, pays, type, top organisations.
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import OrganisationRepository
from app.models.enums import TypeOrganisationEnum


@pytest.mark.asyncio
async def test_get_by_nom_existing(
    async_session: AsyncSession,
    organisation_data: dict
):
    """Test récupération par nom exact."""
    # Arrange
    repository = OrganisationRepository(async_session)
    created = await repository.create(organisation_data)
    
    # Act
    result = await repository.get_by_nom(organisation_data["nom"])
    
    # Assert
    assert result is not None
    assert result.id == created.id
    assert result.nom == organisation_data["nom"]


@pytest.mark.asyncio
async def test_get_by_nom_nonexistent(async_session: AsyncSession):
    """Test récupération par nom inexistant."""
    # Arrange
    repository = OrganisationRepository(async_session)
    
    # Act
    result = await repository.get_by_nom("Nonexistent Organization")
    
    # Assert
    assert result is None


@pytest.mark.asyncio
async def test_search(
    async_session: AsyncSession,
    organisation_data: dict
):
    """Test recherche fuzzy sur nom et nom_court."""
    # Arrange
    repository = OrganisationRepository(async_session)
    await repository.create(organisation_data)
    
    # Act
    results_by_nom = await repository.search("Google")
    results_by_nom_court = await repository.search("Research")
    
    # Assert
    assert len(results_by_nom) >= 1
    assert len(results_by_nom_court) >= 1


@pytest.mark.asyncio
async def test_get_by_country(
    async_session: AsyncSession,
    organisation_data: dict
):
    """Test récupération par code pays."""
    # Arrange
    repository = OrganisationRepository(async_session)
    
    # Créer organisations dans différents pays
    for i, pays in enumerate(["USA", "FRA", "GBR"]):
        data = organisation_data.copy()
        data["nom"] = f"Organization {pays} {i}"
        data["pays"] = pays
        await repository.create(data)
    
    # Act
    usa_orgs = await repository.get_by_country("USA")
    fra_orgs = await repository.get_by_country("FRA")
    
    # Assert
    assert len(usa_orgs) == 1
    assert len(fra_orgs) == 1
    assert usa_orgs[0].pays == "USA"
    assert fra_orgs[0].pays == "FRA"


@pytest.mark.asyncio
async def test_get_by_type(
    async_session: AsyncSession,
    organisation_data: dict
):
    """Test récupération par type d'organisation."""
    # Arrange
    repository = OrganisationRepository(async_session)
    
    # Créer organisations de différents types
    types_and_names = [
        (TypeOrganisationEnum.UNIVERSITY, "MIT"),
        (TypeOrganisationEnum.COMPANY, "Google"),
        (TypeOrganisationEnum.RESEARCH_CENTER, "INRIA"),
    ]
    
    for type_org, nom in types_and_names:
        data = organisation_data.copy()
        data["nom"] = nom
        data["type_organisation"] = type_org
        await repository.create(data)
    
    # Act
    universities = await repository.get_by_type(TypeOrganisationEnum.UNIVERSITY)
    companies = await repository.get_by_type(TypeOrganisationEnum.COMPANY)
    
    # Assert
    assert len(universities) == 1
    assert len(companies) == 1
    assert universities[0].type_organisation == TypeOrganisationEnum.UNIVERSITY
    assert companies[0].type_organisation == TypeOrganisationEnum.COMPANY


@pytest.mark.asyncio
async def test_get_top_by_publications_count(
    async_session: AsyncSession,
    organisation_data: dict
):
    """Test récupération top organisations par nombre de publications."""
    # Arrange
    repository = OrganisationRepository(async_session)
    
    # Créer organisations avec différents nombres de publications
    pub_counts = [100, 500, 1000, 50, 750]
    
    for i, count in enumerate(pub_counts):
        data = organisation_data.copy()
        data["nom"] = f"Organization {i}"
        data["nombre_publications"] = count
        await repository.create(data)
    
    # Act
    top_3 = await repository.get_top_by_publications_count(limit=3)
    
    # Assert
    assert len(top_3) == 3
    org1, count1 = top_3[0]
    org2, count2 = top_3[1]
    org3, count3 = top_3[2]
    
    assert count1 == 1000
    assert count2 == 750
    assert count3 == 500


@pytest.mark.asyncio
async def test_get_by_ranking_range(
    async_session: AsyncSession,
    organisation_data: dict
):
    """Test récupération par plage de classement mondial."""
    # Arrange
    repository = OrganisationRepository(async_session)
    
    # Créer organisations avec différents rankings
    rankings = [1, 10, 50, 100, 200]
    
    for i, rank in enumerate(rankings):
        data = organisation_data.copy()
        data["nom"] = f"Organization {rank}"
        data["ranking_mondial"] = rank
        await repository.create(data)
    
    # Act
    top_50 = await repository.get_by_ranking_range(1, 50)
    mid_range = await repository.get_by_ranking_range(60, 150)
    
    # Assert
    assert len(top_50) == 3  # 1, 10, 50
    assert len(mid_range) == 1  # 100


@pytest.mark.asyncio
async def test_count_by_type(
    async_session: AsyncSession,
    organisation_data: dict
):
    """Test comptage par type d'organisation."""
    # Arrange
    repository = OrganisationRepository(async_session)
    
    # Créer 3 universités et 2 entreprises
    for i in range(3):
        data = organisation_data.copy()
        data["nom"] = f"University {i}"
        data["type_organisation"] = TypeOrganisationEnum.UNIVERSITY
        await repository.create(data)
    
    for i in range(2):
        data = organisation_data.copy()
        data["nom"] = f"Company {i}"
        data["type_organisation"] = TypeOrganisationEnum.COMPANY
        await repository.create(data)
    
    # Act
    uni_count = await repository.count_by_type(TypeOrganisationEnum.UNIVERSITY)
    company_count = await repository.count_by_type(TypeOrganisationEnum.COMPANY)
    
    # Assert
    assert uni_count == 3
    assert company_count == 2


@pytest.mark.asyncio
async def test_count_by_country(
    async_session: AsyncSession,
    organisation_data: dict
):
    """Test comptage par pays."""
    # Arrange
    repository = OrganisationRepository(async_session)
    
    # Créer 3 USA, 2 FRA
    for i in range(3):
        data = organisation_data.copy()
        data["nom"] = f"USA Org {i}"
        data["pays"] = "USA"
        await repository.create(data)
    
    for i in range(2):
        data = organisation_data.copy()
        data["nom"] = f"FRA Org {i}"
        data["pays"] = "FRA"
        await repository.create(data)
    
    # Act
    usa_count = await repository.count_by_country("USA")
    fra_count = await repository.count_by_country("FRA")
    
    # Assert
    assert usa_count == 3
    assert fra_count == 2


@pytest.mark.asyncio
async def test_get_with_publications(
    async_session: AsyncSession,
    created_organisation
):
    """Test eager loading des affiliations."""
    # Arrange
    repository = OrganisationRepository(async_session)
    
    # Act
    result = await repository.get_with_publications(created_organisation.id)
    
    # Assert
    assert result is not None
    assert result.id == created_organisation.id
    assert hasattr(result, 'affiliations')
