"""
Integration tests for Themes API endpoints.

Tests all CRUD operations, validation, and hierarchical features.
"""
import pytest
from httpx import AsyncClient
from uuid import uuid4


# ============================================================================
# CREATE ENDPOINT TESTS (POST /)
# ============================================================================

@pytest.mark.asyncio
async def test_create_theme_success(client: AsyncClient):
    """Test successful theme creation."""
    data = {
        'label': 'Machine Learning',
        'description': 'Algorithms and techniques for learning from data',
        'niveau_hierarchie': 1,
        'chemin_hierarchie': 'Artificial Intelligence/Machine Learning',
        'nombre_publications': 5000
    }

    response = await client.post('/api/v1/themes/', json=data)

    assert response.status_code == 201
    result = response.json()
    assert result['label'] == 'Machine Learning'
    assert result['description'] == 'Algorithms and techniques for learning from data'
    assert result['niveau_hierarchie'] == 1
    assert result['nombre_publications'] == 5000
    assert 'id' in result
    assert 'created_at' in result
    assert 'updated_at' in result


@pytest.mark.asyncio
async def test_create_theme_missing_required_field(client: AsyncClient):
    """Test creation fails when required field (label) is missing."""
    data = {
        'description': 'Theme without label',
        'niveau_hierarchie': 0
        # Missing 'label' (required)
    }

    response = await client.post('/api/v1/themes/', json=data)

    assert response.status_code == 422
    error = response.json()
    assert 'detail' in error


@pytest.mark.asyncio
async def test_create_theme_empty_label_rejected(client: AsyncClient):
    """Test creation fails when label is empty or whitespace."""
    data = {
        'label': '   ',  # Whitespace only
        'niveau_hierarchie': 0
    }

    response = await client.post('/api/v1/themes/', json=data)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_theme_invalid_niveau_hierarchie(client: AsyncClient):
    """Test creation fails when hierarchy level is out of range."""
    data = {
        'label': 'Test Theme',
        'niveau_hierarchie': 15  # Must be between 0 and 10
    }

    response = await client.post('/api/v1/themes/', json=data)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_theme_with_parent(client: AsyncClient):
    """Test creating a child theme with parent_id."""
    # Create parent theme first
    parent_data = {
        'label': 'Parent Theme',
        'niveau_hierarchie': 0
    }
    parent_response = await client.post('/api/v1/themes/', json=parent_data)
    assert parent_response.status_code == 201
    parent = parent_response.json()
    parent_id = parent['id']

    # Create child theme
    child_data = {
        'label': 'Child Theme',
        'niveau_hierarchie': 1,
        'parent_id': parent_id
    }
    response = await client.post('/api/v1/themes/', json=child_data)

    assert response.status_code == 201
    result = response.json()
    assert result['label'] == 'Child Theme'
    assert result['parent_id'] == parent_id


# ============================================================================
# GET ENDPOINT TESTS (GET /{id})
# ============================================================================

@pytest.mark.asyncio
async def test_get_theme_by_id_found(client: AsyncClient):
    """Test retrieving an existing theme by ID."""
    # Create a theme first
    create_data = {
        'label': 'Deep Learning',
        'description': 'Neural networks with multiple layers'
    }
    create_response = await client.post('/api/v1/themes/', json=create_data)
    assert create_response.status_code == 201
    created = create_response.json()
    theme_id = created['id']

    # Retrieve it
    response = await client.get(f'/api/v1/themes/{theme_id}')

    assert response.status_code == 200
    result = response.json()
    assert result['id'] == theme_id
    assert result['label'] == 'Deep Learning'


@pytest.mark.asyncio
async def test_get_theme_by_id_not_found(client: AsyncClient):
    """Test retrieving a non-existent theme returns 404."""
    fake_id = str(uuid4())

    response = await client.get(f'/api/v1/themes/{fake_id}')

    assert response.status_code == 404
    error = response.json()
    assert 'detail' in error
    assert fake_id in error['detail']


# ============================================================================
# LIST ENDPOINT TESTS (GET /)
# ============================================================================

@pytest.mark.asyncio
async def test_list_themes(client: AsyncClient):
    """Test listing themes with default pagination."""
    # Create multiple themes
    for i in range(3):
        data = {
            'label': f'Theme {i+1}',
            'niveau_hierarchie': 0
        }
        await client.post('/api/v1/themes/', json=data)

    # List themes
    response = await client.get('/api/v1/themes/')

    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    assert len(results) >= 3


@pytest.mark.asyncio
async def test_list_themes_with_pagination(client: AsyncClient):
    """Test listing themes with custom pagination."""
    # Create themes
    for i in range(5):
        data = {
            'label': f'Pagination Theme {i+1}',
            'niveau_hierarchie': 0
        }
        await client.post('/api/v1/themes/', json=data)

    # Test with skip and limit
    response = await client.get('/api/v1/themes/?skip=2&limit=2')

    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    assert len(results) <= 2


# ============================================================================
# UPDATE ENDPOINT TESTS (PUT /{id})
# ============================================================================

@pytest.mark.asyncio
async def test_update_theme_success(client: AsyncClient):
    """Test successful theme update."""
    # Create a theme
    create_data = {
        'label': 'Original Label',
        'niveau_hierarchie': 0
    }
    create_response = await client.post('/api/v1/themes/', json=create_data)
    assert create_response.status_code == 201
    created = create_response.json()
    theme_id = created['id']

    # Update it
    update_data = {
        'label': 'Updated Label',
        'description': 'Updated description',
        'nombre_publications': 100
    }
    response = await client.put(f'/api/v1/themes/{theme_id}', json=update_data)

    assert response.status_code == 200
    result = response.json()
    assert result['label'] == 'Updated Label'
    assert result['description'] == 'Updated description'
    assert result['nombre_publications'] == 100


@pytest.mark.asyncio
async def test_update_theme_not_found(client: AsyncClient):
    """Test updating a non-existent theme returns 404."""
    fake_id = str(uuid4())
    update_data = {
        'label': 'Updated Label'
    }

    response = await client.put(f'/api/v1/themes/{fake_id}', json=update_data)

    assert response.status_code == 404
    error = response.json()
    assert 'detail' in error


@pytest.mark.asyncio
async def test_update_theme_invalid_niveau(client: AsyncClient):
    """Test update fails with invalid hierarchy level."""
    # Create a theme
    create_data = {
        'label': 'Test Theme',
        'niveau_hierarchie': 0
    }
    create_response = await client.post('/api/v1/themes/', json=create_data)
    assert create_response.status_code == 201
    created = create_response.json()
    theme_id = created['id']

    # Try to update with invalid hierarchy level
    update_data = {
        'niveau_hierarchie': 20  # Must be between 0 and 10
    }
    response = await client.put(f'/api/v1/themes/{theme_id}', json=update_data)

    assert response.status_code == 422


# ============================================================================
# DELETE ENDPOINT TESTS (DELETE /{id})
# ============================================================================

@pytest.mark.asyncio
async def test_delete_theme_success(client: AsyncClient):
    """Test successful theme deletion."""
    # Create a theme
    create_data = {
        'label': 'Theme to Delete',
        'niveau_hierarchie': 0
    }
    create_response = await client.post('/api/v1/themes/', json=create_data)
    assert create_response.status_code == 201
    created = create_response.json()
    theme_id = created['id']

    # Delete it
    response = await client.delete(f'/api/v1/themes/{theme_id}')

    assert response.status_code == 204

    # Verify it's deleted (should return 404)
    get_response = await client.get(f'/api/v1/themes/{theme_id}')
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_theme_not_found(client: AsyncClient):
    """Test deleting a non-existent theme returns 404."""
    fake_id = str(uuid4())

    response = await client.delete(f'/api/v1/themes/{fake_id}')

    assert response.status_code == 404
    error = response.json()
    assert 'detail' in error
