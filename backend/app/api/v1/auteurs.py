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

@router.get('/', status_code=status.HTTP_200_OK)
async def list_auteurs(
    skip: int = Query(0, ge=0, description='Number of records to skip'),
    limit: int = Query(100, ge=1, le=1000, description='Maximum number of records'),
    search: str = Query(None, description='Search by name (nom, prenom)'),
    sort_by: str = Query('nombre_publications', description='Sort field: nom, h_index, citations, nombre_publications'),
    order: str = Query('desc', description='Sort order: asc or desc'),
    db: AsyncSession = Depends(get_db)
):
    '''
    Retrieve a paginated list of auteurs with search and sorting.

    Parameters:
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 1000)
    - **search**: Search query for name (optional)
    - **sort_by**: Sort field (default: nombre_publications)
    - **order**: Sort order asc/desc (default: desc)

    Returns:
    - List of auteurs with pagination
    '''
    from sqlalchemy import select, desc, asc, or_, func
    from app.models import Auteur

    # Build base query
    stmt = select(Auteur)

    # Apply search filter
    if search:
        search_filter = or_(
            Auteur.nom.ilike(f'%{search}%'),
            Auteur.prenom.ilike(f'%{search}%')
        )
        stmt = stmt.where(search_filter)

    # Apply sorting
    if sort_by == 'h_index':
        order_col = Auteur.h_index
    elif sort_by == 'citations':
        order_col = Auteur.nombre_citations
    elif sort_by == 'nom':
        order_col = Auteur.nom
    else:  # nombre_publications or default
        order_col = Auteur.nombre_publications

    if order == 'asc':
        stmt = stmt.order_by(asc(order_col), Auteur.nom, Auteur.prenom)
    else:
        stmt = stmt.order_by(desc(order_col), Auteur.nom, Auteur.prenom)

    # Count total with same filters
    count_stmt = select(func.count()).select_from(Auteur)
    if search:
        count_stmt = count_stmt.where(or_(
            Auteur.nom.ilike(f'%{search}%'),
            Auteur.prenom.ilike(f'%{search}%')
        ))
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # Apply pagination
    stmt = stmt.offset(skip).limit(limit)

    # Execute query
    result = await db.execute(stmt)
    auteurs = list(result.scalars().all())

    # Calculate pagination
    page = (skip // limit) + 1 if limit > 0 else 1
    total_pages = (total + limit - 1) // limit if total > 0 else 1

    # Transform to response format
    from app.schemas.auteur import AuteurResponse
    items = [AuteurResponse.model_validate(a) for a in auteurs]

    return {
        'items': items,
        'total': total,
        'page': page,
        'limit': limit,
        'total_pages': total_pages
    }


# ============================================================================
# GET BY ID ENDPOINT (GET /{id})
# ============================================================================

@router.get('/{auteur_id}', status_code=status.HTTP_200_OK)
async def get_auteur(
    auteur_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    '''
    Retrieve a specific auteur by ID with full profile (publications, coauthors, stats).

    Parameters:
    - **auteur_id**: UUID of the auteur

    Returns:
    - Complete author profile for frontend

    Raises:
    - 404: Auteur not found
    '''
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.models import Auteur, Publication, PublicationAuteur, PublicationTheme
    from app.schemas.auteur import AuteurResponse
    from collections import defaultdict

    # Load auteur with publications AND themes using eager loading
    stmt = (
        select(Auteur)
        .where(Auteur.id == auteur_id)
        .options(
            selectinload(Auteur.publications)
            .selectinload(PublicationAuteur.publication)
            .selectinload(Publication.themes)
            .selectinload(PublicationTheme.theme)
        )
    )
    result = await db.execute(stmt)
    auteur = result.scalar_one_or_none()

    if not auteur:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Auteur with id {auteur_id} not found'
        )

    # Transform publications from association objects to publication data
    publications = []
    publications_by_year = defaultdict(int)
    publications_by_theme = defaultdict(int)

    for pub_auteur in auteur.publications:
        pub = pub_auteur.publication
        if pub:
            # Extract themes for this publication
            themes = [
                {'id': str(pt.theme.id), 'label': pt.theme.label}
                for pt in pub.themes if pt.theme
            ]

            pub_dict = {
                'id': str(pub.id),
                'titre': pub.titre,
                'abstract': pub.abstract,
                'date_publication': pub.date_publication.isoformat() if pub.date_publication else None,
                'doi': pub.doi,
                'arxiv_id': pub.arxiv_id,
                'url': pub.url,
                'type_publication': pub.type_publication.value if pub.type_publication else 'article',
                'nombre_citations': pub.nombre_citations or 0,
                'themes': themes,  # FIX: Add themes to publication data
            }
            publications.append(pub_dict)

            # Build statistics
            if pub.date_publication:
                year = pub.date_publication.year
                publications_by_year[year] += 1

            # Count themes
            for theme_assoc in pub.themes:
                if theme_assoc.theme:
                    publications_by_theme[theme_assoc.theme.label] += 1

    # Build complete profile response
    auteur_dict = AuteurResponse.model_validate(auteur).model_dump()

    # Add real data for frontend
    auteur_dict['affiliations'] = []  # TODO: Load affiliations when needed
    auteur_dict['publications'] = publications
    auteur_dict['coauthors'] = []  # TODO: Calculate from co-authorship
    auteur_dict['statistics'] = {
        'total_publications': len(publications),
        'total_citations': auteur.nombre_citations,
        'h_index': auteur.h_index,
        'publications_by_year': dict(publications_by_year),
        'citations_by_year': {},  # TODO: Calculate if citation data available
        'publications_by_theme': dict(publications_by_theme)  # FIX: Send all themes, not just top 5
    }

    return auteur_dict


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
