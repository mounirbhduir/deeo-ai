'''
Pydantic schemas for Technologie entity.

This module defines the validation schemas for API requests and responses.
Covers algorithms, frameworks, architectures, tools, libraries, and platforms.
'''

from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.models.enums import TypeTechnologieEnum, NiveauMaturiteEnum


# ============================================================================
# BASE SCHEMA
# ============================================================================

class TechnologieBase(BaseModel):
    '''Base schema with common fields for Technologie.'''

    # Champs obligatoires
    nom: str = Field(..., min_length=1, max_length=255, description='Name of the technology')
    type_technologie: TypeTechnologieEnum = Field(..., description='Type of technology (algorithm, framework, etc.)')
    theme_id: UUID = Field(..., description='Associated research theme ID')

    # Champs optionnels
    description: Optional[str] = Field(None, description='Description of the technology')
    niveau_maturite: Optional[NiveauMaturiteEnum] = Field(None, description='Maturity level (research, production, etc.)')
    popularite: Decimal = Field(default=Decimal('0.0'), ge=0, description='Popularity score')
    url: Optional[str] = Field(None, max_length=500, description='Official website URL')
    github_url: Optional[str] = Field(None, max_length=500, description='GitHub repository URL')

    @field_validator('nom')
    @classmethod
    def nom_must_not_be_empty(cls, v: str) -> str:
        '''Validate that name is not empty or whitespace.'''
        if v and not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        return v.strip()

    @field_validator('url', 'github_url')
    @classmethod
    def url_format(cls, v: Optional[str]) -> Optional[str]:
        '''Validate URL format if present.'''
        if v is None:
            return v
        v = v.strip()
        if not v:
            return None
        # Basic URL validation
        if not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError('URL must start with http:// or https://')
        return v


# ============================================================================
# CREATE SCHEMA (POST)
# ============================================================================

class TechnologieCreate(TechnologieBase):
    '''Schema for creating a new Technologie.

    Used in POST /api/v1/technologies endpoint.
    '''
    pass


# ============================================================================
# UPDATE SCHEMA (PUT/PATCH)
# ============================================================================

class TechnologieUpdate(BaseModel):
    '''Schema for updating an existing Technologie.

    All fields are optional for partial updates.
    Used in PUT/PATCH /api/v1/technologies/{id} endpoint.
    '''

    nom: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    type_technologie: Optional[TypeTechnologieEnum] = None
    theme_id: Optional[UUID] = None
    niveau_maturite: Optional[NiveauMaturiteEnum] = None
    popularite: Optional[Decimal] = Field(None, ge=0)
    url: Optional[str] = Field(None, max_length=500)
    github_url: Optional[str] = Field(None, max_length=500)


# ============================================================================
# RESPONSE SCHEMA (GET)
# ============================================================================

class TechnologieResponse(TechnologieBase):
    '''Schema for Technologie API responses.

    Includes database-generated fields (id, timestamps).
    Used in GET endpoints.
    '''

    id: UUID = Field(..., description='Unique identifier')
    created_at: datetime = Field(..., description='Creation timestamp')
    updated_at: datetime = Field(..., description='Last update timestamp')

    # Configuration Pydantic v2
    model_config = ConfigDict(
        from_attributes=True,  # Permet conversion depuis ORM
        json_schema_extra={
            'example': {
                'id': '550e8400-e29b-41d4-a716-446655440000',
                'nom': 'PyTorch',
                'description': 'Open-source machine learning framework based on Torch',
                'type_technologie': 'framework',
                'theme_id': '450e8400-e29b-41d4-a716-446655440000',
                'niveau_maturite': 'production',
                'popularite': 95.5,
                'url': 'https://pytorch.org',
                'github_url': 'https://github.com/pytorch/pytorch',
                'created_at': '2025-11-17T10:30:00',
                'updated_at': '2025-11-17T10:30:00'
            }
        }
    )
