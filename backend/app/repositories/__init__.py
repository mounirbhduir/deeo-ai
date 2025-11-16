"""
Package repositories - Data Access Layer de DEEO.AI

Implémente le pattern Repository pour abstraire l'accès aux données.

Architecture:
- BaseRepository : Repository générique avec CRUD de base
- XXXRepository : Repositories spécialisés par entité

Usage:
    from app.repositories import PublicationRepository
    
    repository = PublicationRepository(db_session)
    publication = await repository.get_by_doi("10.1234/test")
"""

from .base_repository import BaseRepository
from .publication_repository import PublicationRepository
from .auteur_repository import AuteurRepository
from .organisation_repository import OrganisationRepository
from .theme_repository import ThemeRepository

__all__ = [
    "BaseRepository",
    "PublicationRepository",
    "AuteurRepository",
    "OrganisationRepository",
    "ThemeRepository",
]
