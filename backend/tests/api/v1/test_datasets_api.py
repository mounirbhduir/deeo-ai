"""
Integration tests for Datasets API endpoints.

Tests all CRUD operations and validation.
"""
import pytest
from httpx import AsyncClient
from uuid import uuid4


# ============================================================================
# CREATE ENDPOINT TESTS (POST /)
# ============================================================================

@pytest.mark.asyncio
async def test_create_dataset_success(client: AsyncClient):
    """Test successful dataset creation."""
    data = {
        'nom': 'ImageNet',
        'description': 'Large-scale image classification dataset with 1000 classes',
        'url': 'https://www.image-net.org',
        'taille': '150GB',
        'format': 'JPEG images',
        'date_creation': '2009-01-01'
    }

    response = await client.post('/api/v1/datasets/', json=data)

    assert response.status_code == 201
    result = response.json()
    assert result['nom'] == 'ImageNet'
    assert result['description'] == 'Large-scale image classification dataset with 1000 classes'
    assert result['url'] == 'https://www.image-net.org'
    assert result['taille'] == '150GB'
    assert result['format'] == 'JPEG images'
    assert 'id' in result
    assert 'created_at' in result
    assert 'updated_at' in result


@pytest.mark.asyncio
async def test_create_dataset_missing_required_field(client: AsyncClient):
    """Test creation fails when required field (nom) is missing."""
    data = {
        'description': 'Dataset without name',
        'url': 'https://example.com'
        # Missing 'nom' (required)
    }

    response = await client.post('/api/v1/datasets/', json=data)

    assert response.status_code == 422
    error = response.json()
    assert 'detail' in error


@pytest.mark.asyncio
async def test_create_dataset_empty_nom_rejected(client: AsyncClient):
    """Test creation fails when nom is empty or whitespace."""
    data = {
        'nom': '   ',  # Whitespace only
        'description': 'Test dataset'
    }

    response = await client.post('/api/v1/datasets/', json=data)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_dataset_invalid_url_format(client: AsyncClient):
    """Test creation fails with invalid URL format."""
    data = {
        'nom': 'Test Dataset',
        'url': 'not-a-valid-url'  # Must start with http:// or https://
    }

    response = await client.post('/api/v1/datasets/', json=data)

    assert response.status_code == 422


# ============================================================================
# GET ENDPOINT TESTS (GET /{id})
# ============================================================================

@pytest.mark.asyncio
async def test_get_dataset_by_id_found(client: AsyncClient):
    """Test retrieving an existing dataset by ID."""
    # Create a dataset first
    create_data = {
        'nom': 'MNIST',
        'description': 'Handwritten digits dataset',
        'url': 'http://yann.lecun.com/exdb/mnist/'
    }
    create_response = await client.post('/api/v1/datasets/', json=create_data)
    assert create_response.status_code == 201
    created = create_response.json()
    dataset_id = created['id']

    # Retrieve it
    response = await client.get(f'/api/v1/datasets/{dataset_id}')

    assert response.status_code == 200
    result = response.json()
    assert result['id'] == dataset_id
    assert result['nom'] == 'MNIST'
    assert result['description'] == 'Handwritten digits dataset'


@pytest.mark.asyncio
async def test_get_dataset_by_id_not_found(client: AsyncClient):
    """Test retrieving a non-existent dataset returns 404."""
    fake_id = str(uuid4())

    response = await client.get(f'/api/v1/datasets/{fake_id}')

    assert response.status_code == 404
    error = response.json()
    assert 'detail' in error
    assert fake_id in error['detail']


# ============================================================================
# LIST ENDPOINT TESTS (GET /)
# ============================================================================

@pytest.mark.asyncio
async def test_list_datasets(client: AsyncClient):
    """Test listing datasets with default pagination."""
    # Create multiple datasets
    for i in range(3):
        data = {
            'nom': f'Dataset {i+1}',
            'description': f'Test dataset {i+1}'
        }
        await client.post('/api/v1/datasets/', json=data)

    # List datasets
    response = await client.get('/api/v1/datasets/')

    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    assert len(results) >= 3


@pytest.mark.asyncio
async def test_list_datasets_with_pagination(client: AsyncClient):
    """Test listing datasets with custom pagination."""
    # Create datasets
    for i in range(5):
        data = {
            'nom': f'Pagination Dataset {i+1}',
            'description': f'Test dataset {i+1}'
        }
        await client.post('/api/v1/datasets/', json=data)

    # Test with skip and limit
    response = await client.get('/api/v1/datasets/?skip=2&limit=2')

    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    assert len(results) <= 2


# ============================================================================
# UPDATE ENDPOINT TESTS (PUT /{id})
# ============================================================================

@pytest.mark.asyncio
async def test_update_dataset_success(client: AsyncClient):
    """Test successful dataset update."""
    # Create a dataset
    create_data = {
        'nom': 'Original Dataset Name',
        'description': 'Original description'
    }
    create_response = await client.post('/api/v1/datasets/', json=create_data)
    assert create_response.status_code == 201
    created = create_response.json()
    dataset_id = created['id']

    # Update it
    update_data = {
        'nom': 'Updated Dataset Name',
        'description': 'Updated description',
        'taille': '50GB',
        'format': 'CSV'
    }
    response = await client.put(f'/api/v1/datasets/{dataset_id}', json=update_data)

    assert response.status_code == 200
    result = response.json()
    assert result['nom'] == 'Updated Dataset Name'
    assert result['description'] == 'Updated description'
    assert result['taille'] == '50GB'
    assert result['format'] == 'CSV'


@pytest.mark.asyncio
async def test_update_dataset_not_found(client: AsyncClient):
    """Test updating a non-existent dataset returns 404."""
    fake_id = str(uuid4())
    update_data = {
        'nom': 'Updated Name'
    }

    response = await client.put(f'/api/v1/datasets/{fake_id}', json=update_data)

    assert response.status_code == 404
    error = response.json()
    assert 'detail' in error


@pytest.mark.asyncio
async def test_update_dataset_partial_update(client: AsyncClient):
    """Test partial update of dataset."""
    # Create a dataset
    create_data = {
        'nom': 'Test Dataset',
        'description': 'Test'
    }
    create_response = await client.post('/api/v1/datasets/', json=create_data)
    assert create_response.status_code == 201
    created = create_response.json()
    dataset_id = created['id']

    # Partial update with valid URL
    update_data = {
        'url': 'https://example.com/dataset'
    }
    response = await client.put(f'/api/v1/datasets/{dataset_id}', json=update_data)

    assert response.status_code == 200
    result = response.json()
    assert result['url'] == 'https://example.com/dataset'
    assert result['nom'] == 'Test Dataset'  # Unchanged


# ============================================================================
# DELETE ENDPOINT TESTS (DELETE /{id})
# ============================================================================

@pytest.mark.asyncio
async def test_delete_dataset_success(client: AsyncClient):
    """Test successful dataset deletion."""
    # Create a dataset
    create_data = {
        'nom': 'Dataset to Delete',
        'description': 'This will be deleted'
    }
    create_response = await client.post('/api/v1/datasets/', json=create_data)
    assert create_response.status_code == 201
    created = create_response.json()
    dataset_id = created['id']

    # Delete it
    response = await client.delete(f'/api/v1/datasets/{dataset_id}')

    assert response.status_code == 204

    # Verify it's deleted (should return 404)
    get_response = await client.get(f'/api/v1/datasets/{dataset_id}')
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_dataset_not_found(client: AsyncClient):
    """Test deleting a non-existent dataset returns 404."""
    fake_id = str(uuid4())

    response = await client.delete(f'/api/v1/datasets/{fake_id}')

    assert response.status_code == 404
    error = response.json()
    assert 'detail' in error
