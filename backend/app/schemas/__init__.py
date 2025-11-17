'''
Pydantic schemas for DEEO.AI API.

This package contains validation schemas for all entities.
Provides request/response schemas for FastAPI endpoints.
'''

# Publication schemas
from app.schemas.publication import (
    PublicationBase,
    PublicationCreate,
    PublicationUpdate,
    PublicationResponse
)

# Auteur schemas
from app.schemas.auteur import (
    AuteurBase,
    AuteurCreate,
    AuteurUpdate,
    AuteurResponse
)

# Organisation schemas
from app.schemas.organisation import (
    OrganisationBase,
    OrganisationCreate,
    OrganisationUpdate,
    OrganisationResponse
)

# Theme schemas
from app.schemas.theme import (
    ThemeBase,
    ThemeCreate,
    ThemeUpdate,
    ThemeResponse
)

# Dataset schemas
from app.schemas.dataset import (
    DatasetBase,
    DatasetCreate,
    DatasetUpdate,
    DatasetResponse
)

# Technologie schemas (covers frameworks, tools, algorithms, etc.)
from app.schemas.technologie import (
    TechnologieBase,
    TechnologieCreate,
    TechnologieUpdate,
    TechnologieResponse
)

__all__ = [
    # Publication
    'PublicationBase',
    'PublicationCreate',
    'PublicationUpdate',
    'PublicationResponse',
    # Auteur
    'AuteurBase',
    'AuteurCreate',
    'AuteurUpdate',
    'AuteurResponse',
    # Organisation
    'OrganisationBase',
    'OrganisationCreate',
    'OrganisationUpdate',
    'OrganisationResponse',
    # Theme
    'ThemeBase',
    'ThemeCreate',
    'ThemeUpdate',
    'ThemeResponse',
    # Dataset
    'DatasetBase',
    'DatasetCreate',
    'DatasetUpdate',
    'DatasetResponse',
    # Technologie
    'TechnologieBase',
    'TechnologieCreate',
    'TechnologieUpdate',
    'TechnologieResponse',
]
