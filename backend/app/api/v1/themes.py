'''
API endpoints for Theme management.

This module provides REST API endpoints for CRUD operations on themes.
'''

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.database import get_db
from app.services.theme_service import ThemeService
from app.schemas.theme import (
    ThemeCreate,
    ThemeUpdate,
    ThemeResponse
)

# Router configuration
router = APIRouter(
    prefix='/api/v1/themes',
    tags=['themes']
)


# ============================================================================
# LIST ENDPOINT (GET /)
# ============================================================================

@router.get('/', response_model=List[ThemeResponse], status_code=status.HTTP_200_OK)
async def list_themes(
    skip: int = Query(0, ge=0, description='Number of records to skip'),
    limit: int = Query(100, ge=1, le=1000, description='Maximum number of records'),
    db: AsyncSession = Depends(get_db)
) -> List[ThemeResponse]:
    '''
    Retrieve a paginated list of themes.

    Parameters:
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 1000)

    Returns:
    - List of themes with pagination
    '''
    service = ThemeService(db)
    return await service.get_multi(skip=skip, limit=limit)


# ============================================================================
# GET BY ID ENDPOINT (GET /{id})
# ============================================================================

@router.get('/{theme_id}', response_model=ThemeResponse, status_code=status.HTTP_200_OK)
async def get_theme(
    theme_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> ThemeResponse:
    '''
    Retrieve a specific theme by ID.

    Parameters:
    - **theme_id**: UUID of the theme

    Returns:
    - Theme details

    Raises:
    - 404: Theme not found
    '''
    service = ThemeService(db)
    result = await service.get(theme_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Theme with id {theme_id} not found'
        )
    return result


# ============================================================================
# CREATE ENDPOINT (POST /)
# ============================================================================

@router.post('/', response_model=ThemeResponse, status_code=status.HTTP_201_CREATED)
async def create_theme(
    theme_data: ThemeCreate,
    db: AsyncSession = Depends(get_db)
) -> ThemeResponse:
    '''
    Create a new theme.

    Parameters:
    - **theme_data**: Theme data to create

    Returns:
    - Created theme with generated ID

    Raises:
    - 422: Validation error
    '''
    service = ThemeService(db)
    return await service.create(theme_data.model_dump())


# ============================================================================
# UPDATE ENDPOINT (PUT /{id})
# ============================================================================

@router.put('/{theme_id}', response_model=ThemeResponse, status_code=status.HTTP_200_OK)
async def update_theme(
    theme_id: UUID,
    theme_data: ThemeUpdate,
    db: AsyncSession = Depends(get_db)
) -> ThemeResponse:
    '''
    Update an existing theme (full update).

    Parameters:
    - **theme_id**: UUID of the theme to update
    - **theme_data**: Updated theme data

    Returns:
    - Updated theme

    Raises:
    - 404: Theme not found
    - 422: Validation error
    '''
    service = ThemeService(db)

    # Vérifier existence
    existing = await service.get(theme_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Theme with id {theme_id} not found'
        )

    # Update (seulement champs non-None)
    update_data = theme_data.model_dump(exclude_unset=True)
    result = await service.update(theme_id, update_data)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Theme with id {theme_id} not found'
        )

    return result


# ============================================================================
# DELETE ENDPOINT (DELETE /{id})
# ============================================================================

@router.delete('/{theme_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_theme(
    theme_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> None:
    '''
    Delete a theme (soft delete).

    Parameters:
    - **theme_id**: UUID of the theme to delete

    Raises:
    - 404: Theme not found
    '''
    service = ThemeService(db)

    success = await service.delete(theme_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Theme with id {theme_id} not found'
        )
