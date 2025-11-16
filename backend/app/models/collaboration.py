"""
Modèle SQLAlchemy pour la table collaboration

Collaborations entre organisations de recherche
"""
from sqlalchemy import Column, String, Text, Date, CheckConstraint, ForeignKey, Index, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, UUIDMixin, TimestampMixin
from .enums import TypeCollaborationEnum


class Collaboration(Base, UUIDMixin, TimestampMixin):
    """
    Collaboration entre organisations de recherche.
    
    Exemples : Partenariats académiques, projets industriels, collaborations internationales.
    
    Attributes:
        nom: Nom de la collaboration
        description: Description de la collaboration
        type_collaboration: Type (research, industrial, academic, international, etc.)
        organisation_principale_id: Organisation principale
        date_debut: Date de début
        date_fin: Date de fin (NULL = en cours)
        url: Site web de la collaboration
    """
    __tablename__ = "collaboration"
    
    # Informations principales
    nom = Column(
        String(255),
        nullable=False,
        comment="Nom de la collaboration"
    )
    description = Column(
        Text,
        comment="Description de la collaboration"
    )
    type_collaboration = Column(Enum(TypeCollaborationEnum),
        nullable=False,
        comment="Type de collaboration"
    )
    
    # Organisation principale
    organisation_principale_id = Column(
        UUID(as_uuid=True),
        ForeignKey('organisation.id', ondelete='CASCADE'),
        nullable=False,
        comment="Organisation principale"
    )
    
    # Période
    date_debut = Column(
        Date,
        nullable=False,
        comment="Date de début de la collaboration"
    )
    date_fin = Column(
        Date,
        comment="Date de fin (NULL = en cours)"
    )
    
    # Détails
    url = Column(
        String(500),
        comment="URL du site web de la collaboration"
    )
    
    # Contraintes
    __table_args__ = (
        CheckConstraint('date_fin IS NULL OR date_fin >= date_debut',
                       name='check_collaboration_dates_valid'),
        Index('idx_collaboration_organisation', 'organisation_principale_id'),
        Index('idx_collaboration_type', 'type_collaboration'),
        Index('idx_collaboration_dates', 'date_debut', 'date_fin'),
    )
    
    # Relations
    organisation_principale = relationship(
        "Organisation",
        back_populates="collaborations",
        lazy="select"
    )
    auteurs = relationship(
        "CollaborationAuteur",
        back_populates="collaboration",
        lazy="select"
    )
    organisations_partenaires = relationship(
        "OrganisationCollaboration",
        back_populates="collaboration",
        lazy="select"
    )
    
    def __repr__(self):
        return f"<Collaboration(id={self.id}, nom='{self.nom}', type='{self.type_collaboration.value}')>"
