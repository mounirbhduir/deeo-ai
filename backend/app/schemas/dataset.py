'''
Pydantic schemas for Dataset entity.

This module defines the validation schemas for API requests and responses.
'''

from typing import Optional
from uuid import UUID
from datetime import datetime, date
from pydantic import BaseModel, Field, ConfigDict, field_validator


# ============================================================================
# BASE SCHEMA
# ============================================================================

class DatasetBase(BaseModel):
    '''Base schema with common fields for Dataset.'''

    # Champs obligatoires
    nom: str = Field(..., min_length=1, max_length=255, description='Name of the dataset')

    # Champs optionnels
    description: Optional[str] = Field(None, description='Description of the dataset')
    url: Optional[str] = Field(None, max_length=500, description='Download or documentation URL')
    taille: Optional[str] = Field(None, max_length=50, description='Size of the dataset (e.g., "10GB", "1M samples")')
    format: Optional[str] = Field(None, max_length=100, description='Data format (CSV, JSON, HDF5, etc.)')
    licence_id: Optional[UUID] = Field(None, description='License ID')
    organisation_id: Optional[UUID] = Field(None, description='Creator organization ID')
    date_creation: Optional[date] = Field(None, description='Dataset creation date')

    @field_validator('nom')
    @classmethod
    def nom_must_not_be_empty(cls, v: str) -> str:
        '''Validate that name is not empty or whitespace.'''
        if v and not v.strip():
            raise ValueError('Name cannot be empty or whitespace')
        return v.strip()

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

class DatasetCreate(DatasetBase):
    '''Schema for creating a new Dataset.

    Used in POST /api/v1/datasets endpoint.
    '''
    pass


# ============================================================================
# UPDATE SCHEMA (PUT/PATCH)
# ============================================================================

class DatasetUpdate(BaseModel):
    '''Schema for updating an existing Dataset.

    All fields are optional for partial updates.
    Used in PUT/PATCH /api/v1/datasets/{id} endpoint.
    '''

    nom: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    url: Optional[str] = Field(None, max_length=500)
    taille: Optional[str] = Field(None, max_length=50)
    format: Optional[str] = Field(None, max_length=100)
    licence_id: Optional[UUID] = None
    organisation_id: Optional[UUID] = None
    date_creation: Optional[date] = None


# ============================================================================
# RESPONSE SCHEMA (GET)
# ============================================================================

class DatasetResponse(DatasetBase):
    '''Schema for Dataset API responses.

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
                'nom': 'ImageNet',
                'description': 'Large-scale image classification dataset with 1000 classes',
                'url': 'https://www.image-net.org',
                'taille': '150GB',
                'format': 'JPEG images',
                'licence_id': '450e8400-e29b-41d4-a716-446655440000',
                'organisation_id': '350e8400-e29b-41d4-a716-446655440000',
                'date_creation': '2009-01-01',
                'created_at': '2025-11-17T10:30:00',
                'updated_at': '2025-11-17T10:30:00'
            }
        }
    )
