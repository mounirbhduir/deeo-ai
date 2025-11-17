'''
Pydantic schemas for Organisation entity.

This module defines the validation schemas for API requests and responses.
'''

from typing import Optional
from uuid import UUID
from datetime import datetime
import re
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.models.enums import TypeOrganisationEnum


# ============================================================================
# BASE SCHEMA
# ============================================================================

class OrganisationBase(BaseModel):
    '''Base schema with common fields for Organisation.'''

    # Champs obligatoires
    nom: str = Field(..., min_length=1, max_length=255, description='Full name of the organization')
    type_organisation: TypeOrganisationEnum = Field(..., description='Type of organization')

    # Champs optionnels
    nom_court: Optional[str] = Field(None, max_length=100, description='Acronym or short name')
    pays: Optional[str] = Field(None, max_length=3, description='Country code (ISO 3166-1 alpha-3)')
    ville: Optional[str] = Field(None, max_length=255, description='City')
    secteur: Optional[str] = Field(None, max_length=255, description='Sector/domain')
    url: Optional[str] = Field(None, max_length=500, description='Website URL')
    ranking_mondial: Optional[int] = Field(None, gt=0, description='Global ranking (if applicable)')
    nombre_publications: int = Field(default=0, ge=0, description='Number of publications')
    nombre_chercheurs: int = Field(default=0, ge=0, description='Number of affiliated researchers')

    @field_validator('nom', 'nom_court')
    @classmethod
    def name_must_not_be_empty(cls, v: Optional[str]) -> Optional[str]:
        '''Validate that name is not empty or whitespace.'''
        if v is None:
            return v
        if not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        return v.strip()

    @field_validator('pays')
    @classmethod
    def pays_format(cls, v: Optional[str]) -> Optional[str]:
        '''Validate country code (ISO 3166-1 alpha-3).'''
        if v is None:
            return v
        v = v.strip().upper()
        if not v:
            return None
        # ISO 3166-1 alpha-3: exactly 3 uppercase letters
        pattern = r'^[A-Z]{3}$'
        if not re.match(pattern, v):
            raise ValueError('Country code must be ISO 3166-1 alpha-3 (3 uppercase letters)')
        return v

    @field_validator('url')
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

class OrganisationCreate(OrganisationBase):
    '''Schema for creating a new Organisation.

    Used in POST /api/v1/organisations endpoint.
    '''
    pass


# ============================================================================
# UPDATE SCHEMA (PUT/PATCH)
# ============================================================================

class OrganisationUpdate(BaseModel):
    '''Schema for updating an existing Organisation.

    All fields are optional for partial updates.
    Used in PUT/PATCH /api/v1/organisations/{id} endpoint.
    '''

    nom: Optional[str] = Field(None, min_length=1, max_length=255)
    nom_court: Optional[str] = Field(None, max_length=100)
    type_organisation: Optional[TypeOrganisationEnum] = None
    pays: Optional[str] = Field(None, max_length=3)
    ville: Optional[str] = Field(None, max_length=255)
    secteur: Optional[str] = Field(None, max_length=255)
    url: Optional[str] = Field(None, max_length=500)
    ranking_mondial: Optional[int] = Field(None, gt=0)
    nombre_publications: Optional[int] = Field(None, ge=0)
    nombre_chercheurs: Optional[int] = Field(None, ge=0)


# ============================================================================
# RESPONSE SCHEMA (GET)
# ============================================================================

class OrganisationResponse(OrganisationBase):
    '''Schema for Organisation API responses.

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
                'nom': 'Massachusetts Institute of Technology',
                'nom_court': 'MIT',
                'type_organisation': 'university',
                'pays': 'USA',
                'ville': 'Cambridge',
                'secteur': 'Higher Education & Research',
                'url': 'https://www.mit.edu',
                'ranking_mondial': 1,
                'nombre_publications': 15000,
                'nombre_chercheurs': 450,
                'created_at': '2025-11-17T10:30:00',
                'updated_at': '2025-11-17T10:30:00'
            }
        }
    )
