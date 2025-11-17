'''
API endpoints for Publication management.

This module provides REST API endpoints for CRUD operations on publications.
'''

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.database import get_db
from app.services.publication_service import PublicationService
from app.schemas.publication import (
    PublicationCreate,
    PublicationUpdate,
    PublicationResponse
)

# Router configuration
router = APIRouter(
    prefix='/api/v1/publications',
    tags=['publications']
)


# ============================================================================
# LIST ENDPOINT (GET /)
# ============================================================================

@router.get('/', response_model=List[PublicationResponse], status_code=status.HTTP_200_OK)
async def list_publications(
    skip: int = Query(0, ge=0, description='Number of records to skip'),
    limit: int = Query(100, ge=1, le=1000, description='Maximum number of records'),
    db: AsyncSession = Depends(get_db)
) -> List[PublicationResponse]:
    '''
    Retrieve a paginated list of publications.

    Parameters:
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 1000)

    Returns:
    - List of publications with pagination
    '''
    service = PublicationService(db)
    return await service.get_multi(skip=skip, limit=limit)


# ============================================================================
# GET BY ID ENDPOINT (GET /{id})
# ============================================================================

@router.get('/{publication_id}', response_model=PublicationResponse, status_code=status.HTTP_200_OK)
async def get_publication(
    publication_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> PublicationResponse:
    '''
    Retrieve a specific publication by ID.

    Parameters:
    - **publication_id**: UUID of the publication

    Returns:
    - Publication details

    Raises:
    - 404: Publication not found
    '''
    service = PublicationService(db)
    result = await service.get(publication_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Publication with id {publication_id} not found'
        )
    return result


# ============================================================================
# CREATE ENDPOINT (POST /)
# ============================================================================

@router.post('/', response_model=PublicationResponse, status_code=status.HTTP_201_CREATED)
async def create_publication(
    publication_data: PublicationCreate,
    db: AsyncSession = Depends(get_db)
) -> PublicationResponse:
    '''
    Create a new publication.

    Parameters:
    - **publication_data**: Publication data to create

    Returns:
    - Created publication with generated ID

    Raises:
    - 422: Validation error
    '''
    service = PublicationService(db)
    return await service.create(publication_data.model_dump())


# ============================================================================
# UPDATE ENDPOINT (PUT /{id})
# ============================================================================

@router.put('/{publication_id}', response_model=PublicationResponse, status_code=status.HTTP_200_OK)
async def update_publication(
    publication_id: UUID,
    publication_data: PublicationUpdate,
    db: AsyncSession = Depends(get_db)
) -> PublicationResponse:
    '''
    Update an existing publication (full update).

    Parameters:
    - **publication_id**: UUID of the publication to update
    - **publication_data**: Updated publication data

    Returns:
    - Updated publication

    Raises:
    - 404: Publication not found
    - 422: Validation error
    '''
    service = PublicationService(db)

    # Vérifier existence
    existing = await service.get(publication_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Publication with id {publication_id} not found'
        )

    # Update (seulement champs non-None)
    update_data = publication_data.model_dump(exclude_unset=True)
    result = await service.update(publication_id, update_data)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Publication with id {publication_id} not found'
        )

    return result


# ============================================================================
# DELETE ENDPOINT (DELETE /{id})
# ============================================================================

@router.delete('/{publication_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_publication(
    publication_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> None:
    '''
    Delete a publication (soft delete).

    Parameters:
    - **publication_id**: UUID of the publication to delete

    Raises:
    - 404: Publication not found
    '''
    service = PublicationService(db)

    success = await service.delete(publication_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Publication with id {publication_id} not found'
        )
