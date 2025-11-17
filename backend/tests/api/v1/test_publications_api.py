"""
Integration tests for Publications API endpoints.

Tests all CRUD operations, validation, and specialized endpoints.
"""
import pytest
from httpx import AsyncClient
from datetime import date, timedelta
from uuid import uuid4


# ============================================================================
# CREATE ENDPOINT TESTS (POST /)
# ============================================================================

@pytest.mark.asyncio
async def test_create_publication_success(client: AsyncClient):
    """Test successful publication creation."""
    data = {
        'titre': 'Test Publication: Attention Is All You Need',
        'date_publication': '2024-01-15',
        'type_publication': 'article',
        'abstract': 'This is a test abstract for the publication.',
        'doi': '10.1234/test.2024.001',
        'arxiv_id': '2401.12345',
        'url': 'https://example.com/publication',
        'language': 'en',
        'source_nom': 'arXiv',
        'nombre_citations': 0,
        'nombre_auteurs': 3
    }

    response = await client.post('/api/v1/publications/', json=data)

    assert response.status_code == 201
    result = response.json()
    assert result['titre'] == 'Test Publication: Attention Is All You Need'
    assert result['doi'] == '10.1234/test.2024.001'
    assert result['arxiv_id'] == '2401.12345'
    assert result['type_publication'] == 'article'
    assert 'id' in result
    assert 'created_at' in result
    assert 'updated_at' in result
    assert result['status'] == 'published'  # Default status from model


@pytest.mark.asyncio
async def test_create_publication_missing_required_field(client: AsyncClient):
    """Test creation fails when required field is missing."""
    data = {
        'abstract': 'Abstract without title',
        'doi': '10.1234/test.2024.002'
        # Missing 'titre', 'date_publication', 'type_publication'
    }

    response = await client.post('/api/v1/publications/', json=data)

    assert response.status_code == 422
    error = response.json()
    assert 'detail' in error


@pytest.mark.asyncio
async def test_create_publication_invalid_doi_format(client: AsyncClient):
    """Test creation fails with invalid DOI format."""
    data = {
        'titre': 'Test Publication',
        'date_publication': '2024-01-15',
        'type_publication': 'article',
        'doi': 'INVALID_DOI'  # DOI must start with "10."
    }

    response = await client.post('/api/v1/publications/', json=data)

    assert response.status_code == 422
    error = response.json()
    assert 'detail' in error


@pytest.mark.asyncio
async def test_create_publication_future_date_rejected(client: AsyncClient):
    """Test creation fails when publication date is in the future."""
    future_date = (date.today() + timedelta(days=30)).isoformat()

    data = {
        'titre': 'Future Publication',
        'date_publication': future_date,
        'type_publication': 'article'
    }

    response = await client.post('/api/v1/publications/', json=data)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_publication_empty_titre_rejected(client: AsyncClient):
    """Test creation fails when title is empty or whitespace."""
    data = {
        'titre': '   ',  # Whitespace only
        'date_publication': '2024-01-15',
        'type_publication': 'article'
    }

    response = await client.post('/api/v1/publications/', json=data)

    assert response.status_code == 422


# ============================================================================
# GET ENDPOINT TESTS (GET /{id})
# ============================================================================

@pytest.mark.asyncio
async def test_get_publication_by_id_found(client: AsyncClient):
    """Test retrieving an existing publication by ID."""
    # Create a publication first
    create_data = {
        'titre': 'Publication for GET test',
        'date_publication': '2024-01-15',
        'type_publication': 'article',
        'doi': '10.1234/test.get.001'
    }
    create_response = await client.post('/api/v1/publications/', json=create_data)
    assert create_response.status_code == 201
    created = create_response.json()
    publication_id = created['id']

    # Retrieve it
    response = await client.get(f'/api/v1/publications/{publication_id}')

    assert response.status_code == 200
    result = response.json()
    assert result['id'] == publication_id
    assert result['titre'] == 'Publication for GET test'
    assert result['doi'] == '10.1234/test.get.001'


@pytest.mark.asyncio
async def test_get_publication_by_id_not_found(client: AsyncClient):
    """Test retrieving a non-existent publication returns 404."""
    fake_id = str(uuid4())

    response = await client.get(f'/api/v1/publications/{fake_id}')

    assert response.status_code == 404
    error = response.json()
    assert 'detail' in error
    assert fake_id in error['detail']


# ============================================================================
# LIST ENDPOINT TESTS (GET /)
# ============================================================================

@pytest.mark.asyncio
async def test_list_publications(client: AsyncClient):
    """Test listing publications with default pagination."""
    # Create multiple publications
    for i in range(3):
        data = {
            'titre': f'Publication {i+1}',
            'date_publication': '2024-01-15',
            'type_publication': 'article'
        }
        await client.post('/api/v1/publications/', json=data)

    # List publications
    response = await client.get('/api/v1/publications/')

    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    assert len(results) >= 3


@pytest.mark.asyncio
async def test_list_publications_with_pagination(client: AsyncClient):
    """Test listing publications with custom pagination."""
    # Create publications
    for i in range(5):
        data = {
            'titre': f'Publication Pagination {i+1}',
            'date_publication': '2024-01-15',
            'type_publication': 'article'
        }
        await client.post('/api/v1/publications/', json=data)

    # Test with skip and limit
    response = await client.get('/api/v1/publications/?skip=2&limit=2')

    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    assert len(results) <= 2


# ============================================================================
# UPDATE ENDPOINT TESTS (PUT /{id})
# ============================================================================

@pytest.mark.asyncio
async def test_update_publication_success(client: AsyncClient):
    """Test successful publication update."""
    # Create a publication
    create_data = {
        'titre': 'Original Title',
        'date_publication': '2024-01-15',
        'type_publication': 'article'
    }
    create_response = await client.post('/api/v1/publications/', json=create_data)
    assert create_response.status_code == 201
    created = create_response.json()
    publication_id = created['id']

    # Update it
    update_data = {
        'titre': 'Updated Title',
        'abstract': 'New abstract added',
        'nombre_citations': 10
    }
    response = await client.put(f'/api/v1/publications/{publication_id}', json=update_data)

    assert response.status_code == 200
    result = response.json()
    assert result['titre'] == 'Updated Title'
    assert result['abstract'] == 'New abstract added'
    assert result['nombre_citations'] == 10


@pytest.mark.asyncio
async def test_update_publication_not_found(client: AsyncClient):
    """Test updating a non-existent publication returns 404."""
    fake_id = str(uuid4())
    update_data = {
        'titre': 'Updated Title'
    }

    response = await client.put(f'/api/v1/publications/{fake_id}', json=update_data)

    assert response.status_code == 404
    error = response.json()
    assert 'detail' in error


@pytest.mark.asyncio
async def test_update_publication_partial_update(client: AsyncClient):
    """Test partial update of publication."""
    # Create a publication
    create_data = {
        'titre': 'Test Publication',
        'date_publication': '2024-01-15',
        'type_publication': 'article'
    }
    create_response = await client.post('/api/v1/publications/', json=create_data)
    assert create_response.status_code == 201
    created = create_response.json()
    publication_id = created['id']

    # Partial update with valid DOI
    update_data = {
        'doi': '10.1234/valid.doi'
    }
    response = await client.put(f'/api/v1/publications/{publication_id}', json=update_data)

    assert response.status_code == 200
    result = response.json()
    assert result['doi'] == '10.1234/valid.doi'
    assert result['titre'] == 'Test Publication'  # Unchanged


# ============================================================================
# DELETE ENDPOINT TESTS (DELETE /{id})
# ============================================================================

@pytest.mark.asyncio
async def test_delete_publication_success(client: AsyncClient):
    """Test successful publication deletion."""
    # Create a publication
    create_data = {
        'titre': 'Publication to Delete',
        'date_publication': '2024-01-15',
        'type_publication': 'article'
    }
    create_response = await client.post('/api/v1/publications/', json=create_data)
    assert create_response.status_code == 201
    created = create_response.json()
    publication_id = created['id']

    # Delete it
    response = await client.delete(f'/api/v1/publications/{publication_id}')

    assert response.status_code == 204

    # Verify it's deleted (should return 404)
    get_response = await client.get(f'/api/v1/publications/{publication_id}')
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_publication_not_found(client: AsyncClient):
    """Test deleting a non-existent publication returns 404."""
    fake_id = str(uuid4())

    response = await client.delete(f'/api/v1/publications/{fake_id}')

    assert response.status_code == 404
    error = response.json()
    assert 'detail' in error
