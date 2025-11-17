"""
Integration tests for Auteurs API endpoints.

Tests all CRUD operations, validation, and specialized endpoints.
"""
import pytest
from httpx import AsyncClient
from uuid import uuid4


# ============================================================================
# CREATE ENDPOINT TESTS (POST /)
# ============================================================================

@pytest.mark.asyncio
async def test_create_auteur_success(client: AsyncClient):
    """Test successful auteur creation."""
    data = {
        'nom': 'Vaswani',
        'prenom': 'Ashish',
        'email': 'avaswani@example.com',
        'orcid': '0000-0002-1234-5678',
        'google_scholar_id': 'abc123XYZ',
        'semantic_scholar_id': '123456789',
        'homepage_url': 'https://example.com/avaswani',
        'h_index': 45,
        'nombre_publications': 120,
        'nombre_citations': 25000
    }

    response = await client.post('/api/v1/auteurs/', json=data)

    assert response.status_code == 201
    result = response.json()
    assert result['nom'] == 'Vaswani'
    assert result['prenom'] == 'Ashish'
    assert result['email'] == 'avaswani@example.com'
    assert result['orcid'] == '0000-0002-1234-5678'
    assert result['h_index'] == 45
    assert 'id' in result
    assert 'created_at' in result
    assert 'updated_at' in result


@pytest.mark.asyncio
async def test_create_auteur_missing_required_field(client: AsyncClient):
    """Test creation fails when required field (nom) is missing."""
    data = {
        'prenom': 'John',
        'email': 'john@example.com'
        # Missing 'nom' (required)
    }

    response = await client.post('/api/v1/auteurs/', json=data)

    assert response.status_code == 422
    error = response.json()
    assert 'detail' in error


@pytest.mark.asyncio
async def test_create_auteur_invalid_orcid_format(client: AsyncClient):
    """Test creation fails with invalid ORCID format."""
    data = {
        'nom': 'Doe',
        'prenom': 'John',
        'orcid': 'INVALID-ORCID'  # Must be XXXX-XXXX-XXXX-XXXX
    }

    response = await client.post('/api/v1/auteurs/', json=data)

    assert response.status_code == 422
    error = response.json()
    assert 'detail' in error


@pytest.mark.asyncio
async def test_create_auteur_invalid_email_format(client: AsyncClient):
    """Test creation fails with invalid email format."""
    data = {
        'nom': 'Smith',
        'prenom': 'Jane',
        'email': 'not-an-email'
    }

    response = await client.post('/api/v1/auteurs/', json=data)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_auteur_invalid_url_format(client: AsyncClient):
    """Test creation fails with invalid homepage URL format."""
    data = {
        'nom': 'Johnson',
        'prenom': 'Bob',
        'homepage_url': 'not-a-valid-url'  # Must start with http:// or https://
    }

    response = await client.post('/api/v1/auteurs/', json=data)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_auteur_empty_nom_rejected(client: AsyncClient):
    """Test creation fails when nom is empty or whitespace."""
    data = {
        'nom': '   ',  # Whitespace only
        'prenom': 'Test'
    }

    response = await client.post('/api/v1/auteurs/', json=data)

    assert response.status_code == 422


# ============================================================================
# GET ENDPOINT TESTS (GET /{id})
# ============================================================================

@pytest.mark.asyncio
async def test_get_auteur_by_id_found(client: AsyncClient):
    """Test retrieving an existing auteur by ID."""
    # Create an auteur first
    create_data = {
        'nom': 'Test Author',
        'prenom': 'Get',
        'email': 'gettest@example.com'
    }
    create_response = await client.post('/api/v1/auteurs/', json=create_data)
    assert create_response.status_code == 201
    created = create_response.json()
    auteur_id = created['id']

    # Retrieve it
    response = await client.get(f'/api/v1/auteurs/{auteur_id}')

    assert response.status_code == 200
    result = response.json()
    assert result['id'] == auteur_id
    assert result['nom'] == 'Test Author'
    assert result['prenom'] == 'Get'


@pytest.mark.asyncio
async def test_get_auteur_by_id_not_found(client: AsyncClient):
    """Test retrieving a non-existent auteur returns 404."""
    fake_id = str(uuid4())

    response = await client.get(f'/api/v1/auteurs/{fake_id}')

    assert response.status_code == 404
    error = response.json()
    assert 'detail' in error
    assert fake_id in error['detail']


# ============================================================================
# LIST ENDPOINT TESTS (GET /)
# ============================================================================

@pytest.mark.asyncio
async def test_list_auteurs(client: AsyncClient):
    """Test listing auteurs with default pagination."""
    # Create multiple auteurs
    for i in range(3):
        data = {
            'nom': f'Auteur{i+1}',
            'prenom': f'Test{i+1}'
        }
        await client.post('/api/v1/auteurs/', json=data)

    # List auteurs
    response = await client.get('/api/v1/auteurs/')

    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    assert len(results) >= 3


@pytest.mark.asyncio
async def test_list_auteurs_with_pagination(client: AsyncClient):
    """Test listing auteurs with custom pagination."""
    # Create auteurs
    for i in range(5):
        data = {
            'nom': f'Pagination{i+1}',
            'prenom': f'Test{i+1}'
        }
        await client.post('/api/v1/auteurs/', json=data)

    # Test with skip and limit
    response = await client.get('/api/v1/auteurs/?skip=2&limit=2')

    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    assert len(results) <= 2


# ============================================================================
# UPDATE ENDPOINT TESTS (PUT /{id})
# ============================================================================

@pytest.mark.asyncio
async def test_update_auteur_success(client: AsyncClient):
    """Test successful auteur update."""
    # Create an auteur
    create_data = {
        'nom': 'Original Name',
        'prenom': 'Original First'
    }
    create_response = await client.post('/api/v1/auteurs/', json=create_data)
    assert create_response.status_code == 201
    created = create_response.json()
    auteur_id = created['id']

    # Update it
    update_data = {
        'nom': 'Updated Name',
        'prenom': 'Updated First',
        'email': 'updated@example.com',
        'h_index': 30
    }
    response = await client.put(f'/api/v1/auteurs/{auteur_id}', json=update_data)

    assert response.status_code == 200
    result = response.json()
    assert result['nom'] == 'Updated Name'
    assert result['prenom'] == 'Updated First'
    assert result['email'] == 'updated@example.com'
    assert result['h_index'] == 30


@pytest.mark.asyncio
async def test_update_auteur_not_found(client: AsyncClient):
    """Test updating a non-existent auteur returns 404."""
    fake_id = str(uuid4())
    update_data = {
        'nom': 'Updated Name'
    }

    response = await client.put(f'/api/v1/auteurs/{fake_id}', json=update_data)

    assert response.status_code == 404
    error = response.json()
    assert 'detail' in error


@pytest.mark.asyncio
async def test_update_auteur_partial_update(client: AsyncClient):
    """Test partial update of auteur."""
    # Create an auteur
    create_data = {
        'nom': 'Test Author',
        'prenom': 'Test'
    }
    create_response = await client.post('/api/v1/auteurs/', json=create_data)
    assert create_response.status_code == 201
    created = create_response.json()
    auteur_id = created['id']

    # Partial update with valid ORCID
    update_data = {
        'orcid': '0000-0003-1234-5678'
    }
    response = await client.put(f'/api/v1/auteurs/{auteur_id}', json=update_data)

    assert response.status_code == 200
    result = response.json()
    assert result['orcid'] == '0000-0003-1234-5678'
    assert result['nom'] == 'Test Author'  # Unchanged


# ============================================================================
# DELETE ENDPOINT TESTS (DELETE /{id})
# ============================================================================

@pytest.mark.asyncio
async def test_delete_auteur_success(client: AsyncClient):
    """Test successful auteur deletion."""
    # Create an auteur
    create_data = {
        'nom': 'To Delete',
        'prenom': 'Auteur'
    }
    create_response = await client.post('/api/v1/auteurs/', json=create_data)
    assert create_response.status_code == 201
    created = create_response.json()
    auteur_id = created['id']

    # Delete it
    response = await client.delete(f'/api/v1/auteurs/{auteur_id}')

    assert response.status_code == 204

    # Verify it's deleted (should return 404)
    get_response = await client.get(f'/api/v1/auteurs/{auteur_id}')
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_auteur_not_found(client: AsyncClient):
    """Test deleting a non-existent auteur returns 404."""
    fake_id = str(uuid4())

    response = await client.delete(f'/api/v1/auteurs/{fake_id}')

    assert response.status_code == 404
    error = response.json()
    assert 'detail' in error
