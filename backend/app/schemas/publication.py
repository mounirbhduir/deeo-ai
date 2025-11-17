'''
Pydantic schemas for Publication entity.

This module defines the validation schemas for API requests and responses.
'''

from typing import Optional
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.models.enums import TypePublicationEnum, StatusPublicationEnum


# ============================================================================
# BASE SCHEMA
# ============================================================================

class PublicationBase(BaseModel):
    '''Base schema with common fields for Publication.'''

    # Champs obligatoires
    titre: str = Field(..., min_length=1, max_length=500, description='Title of the publication')
    date_publication: date = Field(..., description='Publication date')
    type_publication: TypePublicationEnum = Field(..., description='Type of publication (article, preprint, etc.)')

    # Champs optionnels
    abstract: Optional[str] = Field(None, description='Abstract/summary of the publication')
    doi: Optional[str] = Field(None, max_length=255, description='Digital Object Identifier (CRITICAL for Phase 3)')
    arxiv_id: Optional[str] = Field(None, max_length=50, description='arXiv identifier (CRITICAL for Phase 3 - alternative to DOI)')
    url: Optional[str] = Field(None, max_length=500, description='URL of the publication')
    language: Optional[str] = Field('en', max_length=10, description='Language code (ISO 639-1)')
    source_nom: Optional[str] = Field(None, max_length=100, description='Source name (arXiv, IEEE, ACM, etc.)')
    nombre_citations: int = Field(default=0, ge=0, description='Number of citations (enriched in Phase 3)')
    nombre_auteurs: int = Field(default=0, ge=0, description='Number of authors')
    score_popularite: Decimal = Field(default=Decimal('0.0'), ge=0, description='Popularity score (calculated)')
    evenement_id: Optional[UUID] = Field(None, description='Associated event ID (if conference/workshop paper)')

    @field_validator('titre')
    @classmethod
    def titre_must_not_be_empty(cls, v: str) -> str:
        '''Validate that title is not empty or whitespace.'''
        if v and not v.strip():
            raise ValueError('Title cannot be empty or whitespace')
        return v.strip()

    @field_validator('doi')
    @classmethod
    def doi_format(cls, v: Optional[str]) -> Optional[str]:
        '''Validate DOI format if present.'''
        if v is None:
            return v
        v = v.strip()
        if not v:
            return None
        # Basic DOI format validation: should start with "10."
        if not v.startswith('10.'):
            raise ValueError('DOI must start with "10."')
        return v

    @field_validator('arxiv_id')
    @classmethod
    def arxiv_id_format(cls, v: Optional[str]) -> Optional[str]:
        '''Validate arXiv ID format if present.'''
        if v is None:
            return v
        v = v.strip()
        if not v:
            return None
        # Basic arXiv format validation: YYMM.NNNNN or arXiv:YYMM.NNNNN
        if v.startswith('arXiv:'):
            v = v[6:]
        return v

    @field_validator('date_publication')
    @classmethod
    def date_not_in_future(cls, v: date) -> date:
        '''Validate that publication date is not in the future.'''
        if v > date.today():
            raise ValueError('Publication date cannot be in the future')
        return v


# ============================================================================
# CREATE SCHEMA (POST)
# ============================================================================

class PublicationCreate(PublicationBase):
    '''Schema for creating a new Publication.

    Used in POST /api/v1/publications endpoint.
    No status field here - defaults to PUBLISHED in the model.
    '''
    pass


# ============================================================================
# UPDATE SCHEMA (PUT/PATCH)
# ============================================================================

class PublicationUpdate(BaseModel):
    '''Schema for updating an existing Publication.

    All fields are optional for partial updates.
    Used in PUT/PATCH /api/v1/publications/{id} endpoint.
    '''

    titre: Optional[str] = Field(None, min_length=1, max_length=500)
    abstract: Optional[str] = None
    doi: Optional[str] = Field(None, max_length=255)
    arxiv_id: Optional[str] = Field(None, max_length=50)
    url: Optional[str] = Field(None, max_length=500)
    date_publication: Optional[date] = None
    type_publication: Optional[TypePublicationEnum] = None
    status: Optional[StatusPublicationEnum] = None
    language: Optional[str] = Field(None, max_length=10)
    source_nom: Optional[str] = Field(None, max_length=100)
    nombre_citations: Optional[int] = Field(None, ge=0)
    nombre_auteurs: Optional[int] = Field(None, ge=0)
    score_popularite: Optional[Decimal] = Field(None, ge=0)
    evenement_id: Optional[UUID] = None


# ============================================================================
# RESPONSE SCHEMA (GET)
# ============================================================================

class PublicationResponse(PublicationBase):
    '''Schema for Publication API responses.

    Includes database-generated fields (id, timestamps, status).
    Used in GET endpoints.
    '''

    id: UUID = Field(..., description='Unique identifier')
    status: StatusPublicationEnum = Field(..., description='Enrichment status (Phase 3 - pipeline)')
    created_at: datetime = Field(..., description='Creation timestamp')
    updated_at: datetime = Field(..., description='Last update timestamp')

    # Configuration Pydantic v2
    model_config = ConfigDict(
        from_attributes=True,  # Permet conversion depuis ORM
        json_schema_extra={
            'example': {
                'id': '550e8400-e29b-41d4-a716-446655440000',
                'titre': 'Attention Is All You Need',
                'abstract': 'The dominant sequence transduction models...',
                'doi': '10.48550/arXiv.1706.03762',
                'arxiv_id': '1706.03762',
                'url': 'https://arxiv.org/abs/1706.03762',
                'date_publication': '2017-06-12',
                'type_publication': 'preprint',
                'status': 'enriched',
                'language': 'en',
                'source_nom': 'arXiv',
                'nombre_citations': 50000,
                'nombre_auteurs': 8,
                'score_popularite': 98.5,
                'evenement_id': None,
                'created_at': '2025-11-17T10:30:00',
                'updated_at': '2025-11-17T10:30:00'
            }
        }
    )
