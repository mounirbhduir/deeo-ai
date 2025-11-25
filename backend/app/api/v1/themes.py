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
# MOCK DATA FOR DEVELOPMENT
# ============================================================================

MOCK_THEMES = [
    {
        "id": "theme-1",
        "label": "Machine Learning",
        "description": "Techniques d'apprentissage automatique permettant aux machines d'apprendre à partir de données",
        "parent_id": None,
        "niveau_hierarchie": 1,
        "chemin_hierarchie": "Machine Learning",
        "nombre_publications": 156,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-11-19T00:00:00Z",
    },
    {
        "id": "theme-2",
        "label": "Natural Language Processing",
        "description": "Traitement automatique du langage naturel pour comprendre et générer du texte",
        "parent_id": None,
        "niveau_hierarchie": 1,
        "chemin_hierarchie": "Natural Language Processing",
        "nombre_publications": 98,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-11-19T00:00:00Z",
    },
    {
        "id": "theme-3",
        "label": "Computer Vision",
        "description": "Vision par ordinateur pour l'analyse et la compréhension d'images et de vidéos",
        "parent_id": None,
        "niveau_hierarchie": 1,
        "chemin_hierarchie": "Computer Vision",
        "nombre_publications": 123,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-11-19T00:00:00Z",
    },
    {
        "id": "theme-4",
        "label": "Robotics",
        "description": "Conception et développement de robots autonomes et intelligents",
        "parent_id": None,
        "niveau_hierarchie": 1,
        "chemin_hierarchie": "Robotics",
        "nombre_publications": 67,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-11-19T00:00:00Z",
    },
    {
        "id": "theme-5",
        "label": "Reinforcement Learning",
        "description": "Apprentissage par renforcement où un agent apprend via interactions avec son environnement",
        "parent_id": None,
        "niveau_hierarchie": 1,
        "chemin_hierarchie": "Reinforcement Learning",
        "nombre_publications": 89,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-11-19T00:00:00Z",
    },
    {
        "id": "theme-6",
        "label": "AI Ethics",
        "description": "Éthique de l'intelligence artificielle, fairness, biais algorithmiques et gouvernance",
        "parent_id": None,
        "niveau_hierarchie": 1,
        "chemin_hierarchie": "AI Ethics",
        "nombre_publications": 45,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-11-19T00:00:00Z",
    },
    {
        "id": "theme-7",
        "label": "Explainable AI",
        "description": "Intelligence artificielle explicable pour comprendre les décisions des modèles",
        "parent_id": None,
        "niveau_hierarchie": 1,
        "chemin_hierarchie": "Explainable AI",
        "nombre_publications": 72,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-11-19T00:00:00Z",
    },
    {
        "id": "theme-8",
        "label": "Generative AI",
        "description": "IA générative pour créer du contenu (texte, images, audio, vidéo)",
        "parent_id": None,
        "niveau_hierarchie": 1,
        "chemin_hierarchie": "Generative AI",
        "nombre_publications": 134,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-11-19T00:00:00Z",
    },
    {
        "id": "theme-9",
        "label": "Neural Networks",
        "description": "Réseaux de neurones artificiels inspirés du cerveau humain",
        "parent_id": None,
        "niveau_hierarchie": 1,
        "chemin_hierarchie": "Neural Networks",
        "nombre_publications": 178,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-11-19T00:00:00Z",
    },
    {
        "id": "theme-10",
        "label": "Transfer Learning",
        "description": "Apprentissage par transfert pour réutiliser des modèles pré-entraînés",
        "parent_id": None,
        "niveau_hierarchie": 1,
        "chemin_hierarchie": "Transfer Learning",
        "nombre_publications": 56,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-11-19T00:00:00Z",
    },
    {
        "id": "theme-11",
        "label": "Federated Learning",
        "description": "Apprentissage fédéré pour entraîner des modèles sur données décentralisées",
        "parent_id": None,
        "niveau_hierarchie": 1,
        "chemin_hierarchie": "Federated Learning",
        "nombre_publications": 38,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-11-19T00:00:00Z",
    },
    {
        "id": "theme-12",
        "label": "Knowledge Graphs",
        "description": "Graphes de connaissances pour représenter et raisonner sur l'information structurée",
        "parent_id": None,
        "niveau_hierarchie": 1,
        "chemin_hierarchie": "Knowledge Graphs",
        "nombre_publications": 63,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-11-19T00:00:00Z",
    },
    # Niveau 2 - Sous-thèmes (exemples)
    {
        "id": "theme-13",
        "label": "Deep Learning",
        "description": "Apprentissage profond avec réseaux de neurones multicouches",
        "parent_id": "theme-1",  # Machine Learning
        "niveau_hierarchie": 2,
        "chemin_hierarchie": "Machine Learning/Deep Learning",
        "nombre_publications": 234,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-11-19T00:00:00Z",
    },
    {
        "id": "theme-14",
        "label": "Transformers",
        "description": "Architecture transformer avec mécanismes d'attention",
        "parent_id": "theme-2",  # NLP
        "niveau_hierarchie": 2,
        "chemin_hierarchie": "Natural Language Processing/Transformers",
        "nombre_publications": 189,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-11-19T00:00:00Z",
    },
    {
        "id": "theme-15",
        "label": "Object Detection",
        "description": "Détection d'objets dans les images",
        "parent_id": "theme-3",  # Computer Vision
        "niveau_hierarchie": 2,
        "chemin_hierarchie": "Computer Vision/Object Detection",
        "nombre_publications": 145,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-11-19T00:00:00Z",
    },
]


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
    Retrieve actual themes from publications (REAL DATA, not mock).
    Returns themes that are actually linked to publications.

    Parameters:
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100, max: 1000)

    Returns:
    - List of real themes used in publications
    '''
    from sqlalchemy import select, func
    from app.models import Theme, PublicationTheme

    # Get themes that are actually used in publications with pub count
    stmt = (
        select(Theme, func.count(PublicationTheme.publication_id).label('nombre_publications'))
        .join(PublicationTheme, PublicationTheme.theme_id == Theme.id)
        .group_by(Theme.id)
        .order_by(func.count(PublicationTheme.publication_id).desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    themes_with_count = result.all()

    # Convert to response format
    themes = []
    for theme, count in themes_with_count:
        theme_dict = {
            'id': str(theme.id),
            'label': theme.label,
            'description': theme.description,
            'parent_id': str(theme.parent_id) if theme.parent_id else None,
            'niveau_hierarchie': theme.niveau_hierarchie or 1,
            'chemin_hierarchie': theme.chemin_hierarchie or theme.label,
            'nombre_publications': count,
            'created_at': theme.created_at.isoformat() if theme.created_at else None,
            'updated_at': theme.updated_at.isoformat() if theme.updated_at else None,
        }
        themes.append(ThemeResponse.model_validate(theme_dict))

    return themes


# ============================================================================
# GET BY ID ENDPOINT (GET /{id})
# ============================================================================

@router.get('/{theme_id}', response_model=ThemeResponse, status_code=status.HTTP_200_OK)
async def get_theme(
    theme_id: str,
) -> ThemeResponse:
    '''
    Retrieve a specific theme by ID.
    Returns mock data for development.

    Parameters:
    - **theme_id**: ID of the theme (e.g., "theme-1")

    Returns:
    - Theme details

    Raises:
    - 404: Theme not found
    '''
    # Find theme in mock data
    theme = next((t for t in MOCK_THEMES if t["id"] == theme_id), None)
    if not theme:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Theme with id {theme_id} not found'
        )
    return theme


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
