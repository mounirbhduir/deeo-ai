'''
API endpoints for Dataset management.

This module provides REST API endpoints for CRUD operations on datasets.
'''

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.database import get_db
from app.models.dataset import Dataset
from app.repositories.base_repository import BaseRepository
from app.services.base_service import BaseService
from app.schemas.dataset import (
    DatasetCreate,
    DatasetUpdate,
    DatasetResponse
)

# Router configuration
router = APIRouter(
    prefix='/api/v1/datasets',
    tags=['datasets']
)


# ============================================================================
# LIST ENDPOINT (GET /)
# ============================================================================

@router.get('/', response_model=List[DatasetResponse], status_code=status.HTTP_200_OK)
async def list_datasets(
    skip: int = Query(0, ge=0, description='Number of records to skip'),
    limit: int = Query(100, ge=1, le=1000, description='Maximum number of records'),
    db: AsyncSession = Depends(get_db)
) -> List[DatasetResponse]:
    '''
    Retrieve a paginated list of datasets.

    Parameters:
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 1000)

    Returns:
    - List of datasets with pagination
    '''
    repository = BaseRepository[Dataset](Dataset, db)
    service = BaseService[Dataset, BaseRepository](repository, db)
    return await service.get_multi(skip=skip, limit=limit)


# ============================================================================
# GET BY ID ENDPOINT (GET /{id})
# ============================================================================

@router.get('/{dataset_id}', response_model=DatasetResponse, status_code=status.HTTP_200_OK)
async def get_dataset(
    dataset_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> DatasetResponse:
    '''
    Retrieve a specific dataset by ID.

    Parameters:
    - **dataset_id**: UUID of the dataset

    Returns:
    - Dataset details

    Raises:
    - 404: Dataset not found
    '''
    repository = BaseRepository[Dataset](Dataset, db)
    service = BaseService[Dataset, BaseRepository](repository, db)
    result = await service.get(dataset_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Dataset with id {dataset_id} not found'
        )
    return result


# ============================================================================
# CREATE ENDPOINT (POST /)
# ============================================================================

@router.post('/', response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def create_dataset(
    dataset_data: DatasetCreate,
    db: AsyncSession = Depends(get_db)
) -> DatasetResponse:
    '''
    Create a new dataset.

    Parameters:
    - **dataset_data**: Dataset data to create

    Returns:
    - Created dataset with generated ID

    Raises:
    - 422: Validation error
    '''
    repository = BaseRepository[Dataset](Dataset, db)
    service = BaseService[Dataset, BaseRepository](repository, db)
    return await service.create(dataset_data.model_dump())


# ============================================================================
# UPDATE ENDPOINT (PUT /{id})
# ============================================================================

@router.put('/{dataset_id}', response_model=DatasetResponse, status_code=status.HTTP_200_OK)
async def update_dataset(
    dataset_id: UUID,
    dataset_data: DatasetUpdate,
    db: AsyncSession = Depends(get_db)
) -> DatasetResponse:
    '''
    Update an existing dataset (full update).

    Parameters:
    - **dataset_id**: UUID of the dataset to update
    - **dataset_data**: Updated dataset data

    Returns:
    - Updated dataset

    Raises:
    - 404: Dataset not found
    - 422: Validation error
    '''
    repository = BaseRepository[Dataset](Dataset, db)
    service = BaseService[Dataset, BaseRepository](repository, db)

    # Vérifier existence
    existing = await service.get(dataset_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Dataset with id {dataset_id} not found'
        )

    # Update (seulement champs non-None)
    update_data = dataset_data.model_dump(exclude_unset=True)
    result = await service.update(dataset_id, update_data)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Dataset with id {dataset_id} not found'
        )

    return result


# ============================================================================
# DELETE ENDPOINT (DELETE /{id})
# ============================================================================

@router.delete('/{dataset_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset(
    dataset_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> None:
    '''
    Delete a dataset (soft delete).

    Parameters:
    - **dataset_id**: UUID of the dataset to delete

    Raises:
    - 404: Dataset not found
    '''
    repository = BaseRepository[Dataset](Dataset, db)
    service = BaseService[Dataset, BaseRepository](repository, db)

    success = await service.delete(dataset_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Dataset with id {dataset_id} not found'
        )
