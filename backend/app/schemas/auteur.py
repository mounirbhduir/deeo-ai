'''
Pydantic schemas for Auteur entity.

This module defines the validation schemas for API requests and responses.
'''

from typing import Optional
from uuid import UUID
from datetime import datetime
import re
from pydantic import BaseModel, Field, ConfigDict, field_validator, EmailStr


# ============================================================================
# BASE SCHEMA
# ============================================================================

class AuteurBase(BaseModel):
    '''Base schema with common fields for Auteur.'''

    # Champs obligatoires
    nom: str = Field(..., min_length=1, max_length=255, description='Last name')

    # Champs optionnels
    prenom: Optional[str] = Field(None, max_length=255, description='First name')
    email: Optional[EmailStr] = Field(None, description='Email address')
    orcid: Optional[str] = Field(None, max_length=19, description='ORCID identifier (format XXXX-XXXX-XXXX-XXXX)')
    google_scholar_id: Optional[str] = Field(None, max_length=50, description='Google Scholar ID')
    semantic_scholar_id: Optional[str] = Field(None, max_length=50, description='Semantic Scholar ID (CRITICAL for Phase 3)')
    homepage_url: Optional[str] = Field(None, max_length=500, description='Personal homepage URL')
    h_index: int = Field(default=0, ge=0, description='H-index (CRITICAL for Phase 3 - updated via Semantic Scholar)')
    nombre_publications: int = Field(default=0, ge=0, description='Number of publications')
    nombre_citations: int = Field(default=0, ge=0, description='Total number of citations')

    @field_validator('nom', 'prenom')
    @classmethod
    def name_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        '''Validate that name is not empty or whitespace.'''
        if v is None:
            return v
        if not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        return v.strip()

    @field_validator('orcid')
    @classmethod
    def orcid_format(cls, v: Optional[str]) -> Optional[str]:
        '''Validate ORCID format (XXXX-XXXX-XXXX-XXXX).'''
        if v is None:
            return v
        v = v.strip()
        if not v:
            return None
        # ORCID format: XXXX-XXXX-XXXX-XXXX (4 groups of 4 digits/X separated by hyphens)
        pattern = r'^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$'
        if not re.match(pattern, v):
            raise ValueError('ORCID must be in format XXXX-XXXX-XXXX-XXXX (digits or X)')
        return v

    @field_validator('homepage_url')
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

class AuteurCreate(AuteurBase):
    '''Schema for creating a new Auteur.

    Used in POST /api/v1/auteurs endpoint.
    '''
    pass


# ============================================================================
# UPDATE SCHEMA (PUT/PATCH)
# ============================================================================

class AuteurUpdate(BaseModel):
    '''Schema for updating an existing Auteur.

    All fields are optional for partial updates.
    Used in PUT/PATCH /api/v1/auteurs/{id} endpoint.
    '''

    nom: Optional[str] = Field(None, min_length=1, max_length=255)
    prenom: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    orcid: Optional[str] = Field(None, max_length=19)
    google_scholar_id: Optional[str] = Field(None, max_length=50)
    semantic_scholar_id: Optional[str] = Field(None, max_length=50)
    homepage_url: Optional[str] = Field(None, max_length=500)
    h_index: Optional[int] = Field(None, ge=0)
    nombre_publications: Optional[int] = Field(None, ge=0)
    nombre_citations: Optional[int] = Field(None, ge=0)


# ============================================================================
# RESPONSE SCHEMA (GET)
# ============================================================================

class AuteurResponse(AuteurBase):
    '''Schema for Auteur API responses.

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
                'nom': 'Vaswani',
                'prenom': 'Ashish',
                'email': 'avaswani@example.com',
                'orcid': '0000-0002-1234-5678',
                'google_scholar_id': 'abc123XYZ',
                'semantic_scholar_id': '123456789',
                'homepage_url': 'https://example.com/avaswani',
                'h_index': 45,
                'nombre_publications': 120,
                'nombre_citations': 25000,
                'created_at': '2025-11-17T10:30:00',
                'updated_at': '2025-11-17T10:30:00'
            }
        }
    )
