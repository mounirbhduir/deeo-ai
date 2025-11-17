'''
API endpoints for Auteur management.

This module provides REST API endpoints for CRUD operations on auteurs.
'''

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.database import get_db
from app.services.auteur_service import AuteurService
from app.schemas.auteur import (
    AuteurCreate,
    AuteurUpdate,
    AuteurResponse
)

# Router configuration
router = APIRouter(
    prefix='/api/v1/auteurs',
    tags=['auteurs']
)


# ============================================================================
# LIST ENDPOINT (GET /)
# ============================================================================

@router.get('/', response_model=List[AuteurResponse], status_code=status.HTTP_200_OK)
async def list_auteurs(
    skip: int = Query(0, ge=0, description='Number of records to skip'),
    limit: int = Query(100, ge=1, le=1000, description='Maximum number of records'),
    db: AsyncSession = Depends(get_db)
) -> List[AuteurResponse]:
    '''
    Retrieve a paginated list of auteurs.

    Parameters:
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 1000)

    Returns:
    - List of auteurs with pagination
    '''
    service = AuteurService(db)
    return await service.get_multi(skip=skip, limit=limit)


# ============================================================================
# GET BY ID ENDPOINT (GET /{id})
# ============================================================================

@router.get('/{auteur_id}', response_model=AuteurResponse, status_code=status.HTTP_200_OK)
async def get_auteur(
    auteur_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> AuteurResponse:
    '''
    Retrieve a specific auteur by ID.

    Parameters:
    - **auteur_id**: UUID of the auteur

    Returns:
    - Auteur details

    Raises:
    - 404: Auteur not found
    '''
    service = AuteurService(db)
    result = await service.get(auteur_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Auteur with id {auteur_id} not found'
        )
    return result


# ============================================================================
# CREATE ENDPOINT (POST /)
# ============================================================================

@router.post('/', response_model=AuteurResponse, status_code=status.HTTP_201_CREATED)
async def create_auteur(
    auteur_data: AuteurCreate,
    db: AsyncSession = Depends(get_db)
) -> AuteurResponse:
    '''
    Create a new auteur.

    Parameters:
    - **auteur_data**: Auteur data to create

    Returns:
    - Created auteur with generated ID

    Raises:
    - 422: Validation error
    '''
    service = AuteurService(db)
    return await service.create(auteur_data.model_dump())


# ============================================================================
# UPDATE ENDPOINT (PUT /{id})
# ============================================================================

@router.put('/{auteur_id}', response_model=AuteurResponse, status_code=status.HTTP_200_OK)
async def update_auteur(
    auteur_id: UUID,
    auteur_data: AuteurUpdate,
    db: AsyncSession = Depends(get_db)
) -> AuteurResponse:
    '''
    Update an existing auteur (full update).

    Parameters:
    - **auteur_id**: UUID of the auteur to update
    - **auteur_data**: Updated auteur data

    Returns:
    - Updated auteur

    Raises:
    - 404: Auteur not found
    - 422: Validation error
    '''
    service = AuteurService(db)

    # Vérifier existence
    existing = await service.get(auteur_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Auteur with id {auteur_id} not found'
        )

    # Update (seulement champs non-None)
    update_data = auteur_data.model_dump(exclude_unset=True)
    result = await service.update(auteur_id, update_data)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Auteur with id {auteur_id} not found'
        )

    return result


# ============================================================================
# DELETE ENDPOINT (DELETE /{id})
# ============================================================================

@router.delete('/{auteur_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_auteur(
    auteur_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> None:
    '''
    Delete a auteur (soft delete).

    Parameters:
    - **auteur_id**: UUID of the auteur to delete

    Raises:
    - 404: Auteur not found
    '''
    service = AuteurService(db)

    success = await service.delete(auteur_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Auteur with id {auteur_id} not found'
        )
