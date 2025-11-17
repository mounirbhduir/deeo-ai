'''
Pydantic schemas for Theme entity.

This module defines the validation schemas for API requests and responses.
'''

from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator


# ============================================================================
# BASE SCHEMA
# ============================================================================

class ThemeBase(BaseModel):
    '''Base schema with common fields for Theme.'''

    # Champs obligatoires
    label: str = Field(..., min_length=1, max_length=255, description='Theme label/name')

    # Champs optionnels
    description: Optional[str] = Field(None, description='Description of the theme')
    niveau_hierarchie: int = Field(default=0, ge=0, le=10, description='Hierarchy level (0 = root)')
    parent_id: Optional[UUID] = Field(None, description='Parent theme ID (NULL = root theme)')
    chemin_hierarchie: Optional[str] = Field(None, description='Full hierarchical path (e.g., "AI/ML/Deep Learning")')
    nombre_publications: int = Field(default=0, ge=0, description='Number of associated publications')

    @field_validator('label')
    @classmethod
    def label_must_not_be_empty(cls, v: str) -> str:
        '''Validate that label is not empty or whitespace.'''
        if v and not v.strip():
            raise ValueError('Label cannot be empty or whitespace')
        return v.strip()

    @field_validator('niveau_hierarchie')
    @classmethod
    def niveau_in_range(cls, v: int) -> int:
        '''Validate that hierarchy level is between 0 and 10.'''
        if not (0 <= v <= 10):
            raise ValueError('Hierarchy level must be between 0 and 10')
        return v


# ============================================================================
# CREATE SCHEMA (POST)
# ============================================================================

class ThemeCreate(ThemeBase):
    '''Schema for creating a new Theme.

    Used in POST /api/v1/themes endpoint.
    '''
    pass


# ============================================================================
# UPDATE SCHEMA (PUT/PATCH)
# ============================================================================

class ThemeUpdate(BaseModel):
    '''Schema for updating an existing Theme.

    All fields are optional for partial updates.
    Used in PUT/PATCH /api/v1/themes/{id} endpoint.
    '''

    label: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    niveau_hierarchie: Optional[int] = Field(None, ge=0, le=10)
    parent_id: Optional[UUID] = None
    chemin_hierarchie: Optional[str] = None
    nombre_publications: Optional[int] = Field(None, ge=0)


# ============================================================================
# RESPONSE SCHEMA (GET)
# ============================================================================

class ThemeResponse(ThemeBase):
    '''Schema for Theme API responses.

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
                'label': 'Machine Learning',
                'description': 'Algorithms and techniques for learning from data',
                'niveau_hierarchie': 1,
                'parent_id': '450e8400-e29b-41d4-a716-446655440000',
                'chemin_hierarchie': 'Artificial Intelligence/Machine Learning',
                'nombre_publications': 5000,
                'created_at': '2025-11-17T10:30:00',
                'updated_at': '2025-11-17T10:30:00'
            }
        }
    )
