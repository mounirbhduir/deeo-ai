"""
Package models - Tous les modèles SQLAlchemy de DEEO.AI

Import dans l'ordre des dépendances pour Alembic.
"""

# Base classes
from .base import Base, TimestampMixin, UUIDMixin
from .enums import (
    TypeOrganisationEnum,
    TypePublicationEnum,
    TypeTechnologieEnum,
    NiveauMaturiteEnum,
    TypeLicenceEnum,
    TypeEvenementEnum,
    StatutEvenementEnum,
    TypeImpactEnum,
    NiveauImpactEnum,
    TypeMetriqueEnum,
    TypeCollaborationEnum,
    StatusPublicationEnum,
)

# Tables principales (ordre des dépendances)
from .source import Source
from .licence import Licence
from .theme import Theme
from .organisation import Organisation
from .evenement import Evenement
from .auteur import Auteur
from .publication import Publication  # Hub central
from .technologie import Technologie
from .dataset import Dataset
from .outil import Outil
from .collaboration import Collaboration
from .impact_societal import ImpactSocietal
from .metrique_engagement import MetriqueEngagement
from .changement_metadonnees import ChangementMetadonnees

# Tables d'association N-N
from .publication_auteur import PublicationAuteur
from .publication_theme import PublicationTheme
from .publication_technologie import PublicationTechnologie
from .publication_dataset import PublicationDataset
from .publication_outil import PublicationOutil
from .citation import Citation
from .affiliation import Affiliation
from .collaboration_auteur import CollaborationAuteur
from .technologie_dataset import TechnologieDataset
from .technologie_outil import TechnologieOutil
from .organisation_collaboration import OrganisationCollaboration
from .auteur_metrique import AuteurMetrique
from .publication_impact import PublicationImpact
from .publication_metrique import PublicationMetrique

# Export all models
__all__ = [
    # Base
    "Base",
    "TimestampMixin",
    "UUIDMixin",
    # Enums
    "TypeOrganisationEnum",
    "TypePublicationEnum",
    "TypeTechnologieEnum",
    "NiveauMaturiteEnum",
    "TypeLicenceEnum",
    "TypeEvenementEnum",
    "StatutEvenementEnum",
    "TypeImpactEnum",
    "NiveauImpactEnum",
    "TypeMetriqueEnum",
    "TypeCollaborationEnum",
    "StatusPublicationEnum",
    # Tables principales
    "Source",
    "Licence",
    "Theme",
    "Organisation",
    "Evenement",
    "Auteur",
    "Publication",
    "Technologie",
    "Dataset",
    "Outil",
    "Collaboration",
    "ImpactSocietal",
    "MetriqueEngagement",
    "ChangementMetadonnees",
    # Tables d'association
    "PublicationAuteur",
    "PublicationTheme",
    "PublicationTechnologie",
    "PublicationDataset",
    "PublicationOutil",
    "Citation",
    "Affiliation",
    "CollaborationAuteur",
    "TechnologieDataset",
    "TechnologieOutil",
    "OrganisationCollaboration",
    "AuteurMetrique",
    "PublicationImpact",
    "PublicationMetrique",
]
