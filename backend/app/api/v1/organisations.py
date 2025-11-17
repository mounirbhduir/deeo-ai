'''
API endpoints for Organisation management.

This module provides REST API endpoints for CRUD operations on organisations.
'''

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.database import get_db
from app.services.organisation_service import OrganisationService
from app.schemas.organisation import (
    OrganisationCreate,
    OrganisationUpdate,
    OrganisationResponse
)

# Router configuration
router = APIRouter(
    prefix='/api/v1/organisations',
    tags=['organisations']
)


# ============================================================================
# LIST ENDPOINT (GET /)
# ============================================================================

@router.get('/', response_model=List[OrganisationResponse], status_code=status.HTTP_200_OK)
async def list_organisations(
    skip: int = Query(0, ge=0, description='Number of records to skip'),
    limit: int = Query(100, ge=1, le=1000, description='Maximum number of records'),
    db: AsyncSession = Depends(get_db)
) -> List[OrganisationResponse]:
    '''
    Retrieve a paginated list of organisations.

    Parameters:
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 1000)

    Returns:
    - List of organisations with pagination
    '''
    service = OrganisationService(db)
    return await service.get_multi(skip=skip, limit=limit)


# ============================================================================
# GET BY ID ENDPOINT (GET /{id})
# ============================================================================

@router.get('/{organisation_id}', response_model=OrganisationResponse, status_code=status.HTTP_200_OK)
async def get_organisation(
    organisation_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> OrganisationResponse:
    '''
    Retrieve a specific organisation by ID.

    Parameters:
    - **organisation_id**: UUID of the organisation

    Returns:
    - Organisation details

    Raises:
    - 404: Organisation not found
    '''
    service = OrganisationService(db)
    result = await service.get(organisation_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Organisation with id {organisation_id} not found'
        )
    return result


# ============================================================================
# CREATE ENDPOINT (POST /)
# ============================================================================

@router.post('/', response_model=OrganisationResponse, status_code=status.HTTP_201_CREATED)
async def create_organisation(
    organisation_data: OrganisationCreate,
    db: AsyncSession = Depends(get_db)
) -> OrganisationResponse:
    '''
    Create a new organisation.

    Parameters:
    - **organisation_data**: Organisation data to create

    Returns:
    - Created organisation with generated ID

    Raises:
    - 422: Validation error
    '''
    service = OrganisationService(db)
    return await service.create(organisation_data.model_dump())


# ============================================================================
# UPDATE ENDPOINT (PUT /{id})
# ============================================================================

@router.put('/{organisation_id}', response_model=OrganisationResponse, status_code=status.HTTP_200_OK)
async def update_organisation(
    organisation_id: UUID,
    organisation_data: OrganisationUpdate,
    db: AsyncSession = Depends(get_db)
) -> OrganisationResponse:
    '''
    Update an existing organisation (full update).

    Parameters:
    - **organisation_id**: UUID of the organisation to update
    - **organisation_data**: Updated organisation data

    Returns:
    - Updated organisation

    Raises:
    - 404: Organisation not found
    - 422: Validation error
    '''
    service = OrganisationService(db)

    # Vérifier existence
    existing = await service.get(organisation_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Organisation with id {organisation_id} not found'
        )

    # Update (seulement champs non-None)
    update_data = organisation_data.model_dump(exclude_unset=True)
    result = await service.update(organisation_id, update_data)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Organisation with id {organisation_id} not found'
        )

    return result


# ============================================================================
# DELETE ENDPOINT (DELETE /{id})
# ============================================================================

@router.delete('/{organisation_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_organisation(
    organisation_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> None:
    '''
    Delete a organisation (soft delete).

    Parameters:
    - **organisation_id**: UUID of the organisation to delete

    Raises:
    - 404: Organisation not found
    '''
    service = OrganisationService(db)

    success = await service.delete(organisation_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Organisation with id {organisation_id} not found'
        )
