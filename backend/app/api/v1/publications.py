'''
API endpoints for Publication management.

This module provides REST API endpoints for CRUD operations on publications.
'''

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from typing import List, Dict, Any, Optional
from uuid import UUID

from app.database import get_db
from app.services.publication_service import PublicationService
from app.repositories.publication_repository import PublicationRepository
from app.models import Publication, PublicationAuteur, PublicationTheme
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
# SEARCH ENDPOINT (GET /search) - With relations for frontend
# ============================================================================

@router.get('/search/{publication_id}', status_code=status.HTTP_200_OK)
async def get_publication_detail(
    publication_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    '''Get a single publication by ID with full details.'''
    repo = PublicationRepository(db)

    # Get publication with relations
    stmt = (
        select(Publication)
        .where(Publication.id == publication_id)
        .options(
            selectinload(Publication.auteurs).selectinload(PublicationAuteur.auteur),
            selectinload(Publication.themes).selectinload(PublicationTheme.theme)
        )
    )
    result = await db.execute(stmt)
    pub = result.scalar_one_or_none()

    if not pub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Publication with id {publication_id} not found'
        )

    # Transform to frontend format
    item = {
        'id': str(pub.id),
        'titre': pub.titre,
        'abstract': pub.abstract,
        'date_publication': pub.date_publication.isoformat() if pub.date_publication else None,
        'doi': pub.doi,
        'arxiv_id': pub.arxiv_id,
        'url': pub.url,
        'type_publication': pub.type_publication or 'article',
        'nombre_citations': pub.nombre_citations or 0,
        'auteurs': [
            {
                'id': str(pa.auteur_id),
                'nom': pa.auteur.nom if pa.auteur else 'Unknown',
                'prenom': pa.auteur.prenom if pa.auteur else ''
            }
            for pa in pub.auteurs
        ] if pub.auteurs else [],
        'themes': [
            {'id': str(pt.theme.id), 'label': pt.theme.label}
            for pt in pub.themes if pt.theme
        ] if pub.themes else [],
        'organisations': []
    }

    return item


@router.get('/search', status_code=status.HTTP_200_OK)
async def search_publications(
    page: int = Query(1, ge=1, description='Page number'),
    limit: int = Query(20, ge=1, le=1000, description='Items per page'),
    q: Optional[str] = Query(None, description='Search query (titre, abstract)'),
    theme: Optional[str] = Query(None, description='Filter by theme ID'),
    type: Optional[str] = Query(None, description='Filter by publication type'),
    sort_by: str = Query('date', description='Sort field: date, citations, relevance'),
    sort_order: str = Query('desc', description='Sort order: asc or desc'),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    '''Search publications with authors and themes loaded.'''
    skip = (page - 1) * limit

    # Build query with filters
    from sqlalchemy import desc, asc, or_, distinct
    from app.models import PublicationTheme, Theme, Auteur

    stmt = select(Publication).options(
        selectinload(Publication.auteurs).selectinload(PublicationAuteur.auteur),
        selectinload(Publication.themes).selectinload(PublicationTheme.theme)
    )

    # Apply text search filter (including author names)
    if q:
        # Join with auteurs to search by author name
        stmt = stmt.outerjoin(Publication.auteurs).outerjoin(PublicationAuteur.auteur)
        search_filter = or_(
            Publication.titre.ilike(f'%{q}%'),
            Publication.abstract.ilike(f'%{q}%'),
            Auteur.nom.ilike(f'%{q}%'),
            Auteur.prenom.ilike(f'%{q}%')
        )
        stmt = stmt.where(search_filter).distinct()

    # Apply theme filter
    # DEFENSIVE: Handle UUID, string ID (theme-1), or label (Machine Learning)
    if theme:
        try:
            # Try to use as UUID
            from uuid import UUID as UUIDType
            from sqlalchemy import cast, Text
            UUIDType(theme)  # Validate UUID
            stmt = stmt.join(Publication.themes).join(PublicationTheme.theme).where(Theme.id == theme)
        except (ValueError, AttributeError):
            # If not UUID, search by ID string OR label (cast ID to text for comparison)
            from sqlalchemy import cast, Text
            stmt = stmt.join(Publication.themes).join(PublicationTheme.theme).where(
                or_(cast(Theme.id, Text) == theme, Theme.label.ilike(f'%{theme}%'))
            )

    # Apply type filter
    if type:
        stmt = stmt.where(Publication.type_publication == type)

    # Apply sorting
    if sort_by == 'citations':
        order_col = Publication.nombre_citations
    elif sort_by == 'date':
        order_col = Publication.date_publication
    else:  # relevance or default
        order_col = Publication.date_publication

    if sort_order == 'asc':
        stmt = stmt.order_by(asc(order_col))
    else:
        stmt = stmt.order_by(desc(order_col))

    # Apply pagination
    stmt = stmt.offset(skip).limit(limit)

    # Execute query
    result = await db.execute(stmt)
    publications = list(result.unique().scalars().all())

    # Count total with same filters (including author name search)
    count_stmt = select(func.count(distinct(Publication.id))).select_from(Publication)
    if q:
        # Join with auteurs for author name search in count
        count_stmt = count_stmt.outerjoin(Publication.auteurs).outerjoin(PublicationAuteur.auteur)
        count_stmt = count_stmt.where(or_(
            Publication.titre.ilike(f'%{q}%'),
            Publication.abstract.ilike(f'%{q}%'),
            Auteur.nom.ilike(f'%{q}%'),
            Auteur.prenom.ilike(f'%{q}%')
        ))
    # DEFENSIVE: Same theme filter logic as above
    if theme:
        try:
            from uuid import UUID as UUIDType
            from sqlalchemy import cast, Text
            UUIDType(theme)
            count_stmt = count_stmt.join(Publication.themes).join(PublicationTheme.theme).where(Theme.id == theme)
        except (ValueError, AttributeError):
            from sqlalchemy import cast, Text
            count_stmt = count_stmt.join(Publication.themes).join(PublicationTheme.theme).where(
                or_(cast(Theme.id, Text) == theme, Theme.label.ilike(f'%{theme}%'))
            )
    if type:
        count_stmt = count_stmt.where(Publication.type_publication == type)

    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # Transform to frontend format
    items = []
    for pub in publications:
        item = {
            'id': str(pub.id),
            'titre': pub.titre,
            'abstract': pub.abstract,
            'date_publication': pub.date_publication.isoformat() if pub.date_publication else None,
            'doi': pub.doi,
            'arxiv_id': pub.arxiv_id,
            'url': pub.url,
            'type_publication': pub.type_publication or 'article',
            'nombre_citations': pub.nombre_citations or 0,
            'auteurs': [
                {
                    'id': str(pa.auteur_id),
                    'nom': pa.auteur.nom if pa.auteur else 'Unknown',
                    'prenom': pa.auteur.prenom if pa.auteur else ''
                }
                for pa in pub.auteurs
            ] if pub.auteurs else [],
            'themes': [
                {'id': str(pt.theme.id), 'label': pt.theme.label}
                for pt in pub.themes if pt.theme
            ] if pub.themes else [],
            'organisations': []
        }
        items.append(item)

    total_pages = (total + limit - 1) // limit if total > 0 else 1

    return {
        'items': items,
        'total': total,
        'page': page,
        'per_page': limit,
        'total_pages': total_pages
    }


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
