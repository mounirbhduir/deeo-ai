"""
Integration tests for Organisations API endpoints.

Tests all CRUD operations, validation, and specialized endpoints.
"""
import pytest
from httpx import AsyncClient
from uuid import uuid4


# ============================================================================
# CREATE ENDPOINT TESTS (POST /)
# ============================================================================

@pytest.mark.asyncio
async def test_create_organisation_success(client: AsyncClient):
    """Test successful organisation creation."""
    data = {
        'nom': 'Massachusetts Institute of Technology',
        'nom_court': 'MIT',
        'type_organisation': 'university',
        'pays': 'USA',
        'ville': 'Cambridge',
        'secteur': 'Higher Education & Research',
        'url': 'https://www.mit.edu',
        'ranking_mondial': 1,
        'nombre_publications': 15000,
        'nombre_chercheurs': 450
    }

    response = await client.post('/api/v1/organisations/', json=data)

    assert response.status_code == 201
    result = response.json()
    assert result['nom'] == 'Massachusetts Institute of Technology'
    assert result['nom_court'] == 'MIT'
    assert result['type_organisation'] == 'university'
    assert result['pays'] == 'USA'
    assert result['ranking_mondial'] == 1
    assert 'id' in result
    assert 'created_at' in result
    assert 'updated_at' in result


@pytest.mark.asyncio
async def test_create_organisation_missing_required_field(client: AsyncClient):
    """Test creation fails when required fields are missing."""
    data = {
        'nom_court': 'MIT',
        'pays': 'USA'
        # Missing 'nom' and 'type_organisation' (required)
    }

    response = await client.post('/api/v1/organisations/', json=data)

    assert response.status_code == 422
    error = response.json()
    assert 'detail' in error


@pytest.mark.asyncio
async def test_create_organisation_invalid_pays_format(client: AsyncClient):
    """Test creation fails with invalid country code format."""
    data = {
        'nom': 'Test University',
        'type_organisation': 'university',
        'pays': 'US'  # Should be 3 letters (ISO 3166-1 alpha-3)
    }

    response = await client.post('/api/v1/organisations/', json=data)

    assert response.status_code == 422
    error = response.json()
    assert 'detail' in error


@pytest.mark.asyncio
async def test_create_organisation_invalid_url_format(client: AsyncClient):
    """Test creation fails with invalid URL format."""
    data = {
        'nom': 'Test University',
        'type_organisation': 'university',
        'url': 'not-a-valid-url'  # Must start with http:// or https://
    }

    response = await client.post('/api/v1/organisations/', json=data)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_organisation_empty_nom_rejected(client: AsyncClient):
    """Test creation fails when nom is empty or whitespace."""
    data = {
        'nom': '   ',  # Whitespace only
        'type_organisation': 'university'
    }

    response = await client.post('/api/v1/organisations/', json=data)

    assert response.status_code == 422


# ============================================================================
# GET ENDPOINT TESTS (GET /{id})
# ============================================================================

@pytest.mark.asyncio
async def test_get_organisation_by_id_found(client: AsyncClient):
    """Test retrieving an existing organisation by ID."""
    # Create an organisation first
    create_data = {
        'nom': 'Stanford University',
        'type_organisation': 'university',
        'pays': 'USA'
    }
    create_response = await client.post('/api/v1/organisations/', json=create_data)
    assert create_response.status_code == 201
    created = create_response.json()
    organisation_id = created['id']

    # Retrieve it
    response = await client.get(f'/api/v1/organisations/{organisation_id}')

    assert response.status_code == 200
    result = response.json()
    assert result['id'] == organisation_id
    assert result['nom'] == 'Stanford University'
    assert result['type_organisation'] == 'university'


@pytest.mark.asyncio
async def test_get_organisation_by_id_not_found(client: AsyncClient):
    """Test retrieving a non-existent organisation returns 404."""
    fake_id = str(uuid4())

    response = await client.get(f'/api/v1/organisations/{fake_id}')

    assert response.status_code == 404
    error = response.json()
    assert 'detail' in error
    assert fake_id in error['detail']


# ============================================================================
# LIST ENDPOINT TESTS (GET /)
# ============================================================================

@pytest.mark.asyncio
async def test_list_organisations(client: AsyncClient):
    """Test listing organisations with default pagination."""
    # Create multiple organisations
    for i in range(3):
        data = {
            'nom': f'University {i+1}',
            'type_organisation': 'university'
        }
        await client.post('/api/v1/organisations/', json=data)

    # List organisations
    response = await client.get('/api/v1/organisations/')

    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    assert len(results) >= 3


@pytest.mark.asyncio
async def test_list_organisations_with_pagination(client: AsyncClient):
    """Test listing organisations with custom pagination."""
    # Create organisations
    for i in range(5):
        data = {
            'nom': f'Research Institute {i+1}',
            'type_organisation': 'research_institute'
        }
        await client.post('/api/v1/organisations/', json=data)

    # Test with skip and limit
    response = await client.get('/api/v1/organisations/?skip=2&limit=2')

    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    assert len(results) <= 2


# ============================================================================
# UPDATE ENDPOINT TESTS (PUT /{id})
# ============================================================================

@pytest.mark.asyncio
async def test_update_organisation_success(client: AsyncClient):
    """Test successful organisation update."""
    # Create an organisation
    create_data = {
        'nom': 'Original University Name',
        'type_organisation': 'university'
    }
    create_response = await client.post('/api/v1/organisations/', json=create_data)
    assert create_response.status_code == 201
    created = create_response.json()
    organisation_id = created['id']

    # Update it
    update_data = {
        'nom': 'Updated University Name',
        'nom_court': 'UUN',
        'pays': 'FRA',
        'ranking_mondial': 50
    }
    response = await client.put(f'/api/v1/organisations/{organisation_id}', json=update_data)

    assert response.status_code == 200
    result = response.json()
    assert result['nom'] == 'Updated University Name'
    assert result['nom_court'] == 'UUN'
    assert result['pays'] == 'FRA'
    assert result['ranking_mondial'] == 50


@pytest.mark.asyncio
async def test_update_organisation_not_found(client: AsyncClient):
    """Test updating a non-existent organisation returns 404."""
    fake_id = str(uuid4())
    update_data = {
        'nom': 'Updated Name'
    }

    response = await client.put(f'/api/v1/organisations/{fake_id}', json=update_data)

    assert response.status_code == 404
    error = response.json()
    assert 'detail' in error


@pytest.mark.asyncio
async def test_update_organisation_invalid_pays(client: AsyncClient):
    """Test update fails with invalid country code format."""
    # Create an organisation
    create_data = {
        'nom': 'Test University',
        'type_organisation': 'university'
    }
    create_response = await client.post('/api/v1/organisations/', json=create_data)
    assert create_response.status_code == 201
    created = create_response.json()
    organisation_id = created['id']

    # Try to update with invalid country code
    update_data = {
        'pays': 'INVALID'  # Should be 3 letters
    }
    response = await client.put(f'/api/v1/organisations/{organisation_id}', json=update_data)

    assert response.status_code == 422


# ============================================================================
# DELETE ENDPOINT TESTS (DELETE /{id})
# ============================================================================

@pytest.mark.asyncio
async def test_delete_organisation_success(client: AsyncClient):
    """Test successful organisation deletion."""
    # Create an organisation
    create_data = {
        'nom': 'Organisation to Delete',
        'type_organisation': 'company'
    }
    create_response = await client.post('/api/v1/organisations/', json=create_data)
    assert create_response.status_code == 201
    created = create_response.json()
    organisation_id = created['id']

    # Delete it
    response = await client.delete(f'/api/v1/organisations/{organisation_id}')

    assert response.status_code == 204

    # Verify it's deleted (should return 404)
    get_response = await client.get(f'/api/v1/organisations/{organisation_id}')
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_organisation_not_found(client: AsyncClient):
    """Test deleting a non-existent organisation returns 404."""
    fake_id = str(uuid4())

    response = await client.delete(f'/api/v1/organisations/{fake_id}')

    assert response.status_code == 404
    error = response.json()
    assert 'detail' in error
