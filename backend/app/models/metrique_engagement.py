"""
Modèle SQLAlchemy pour la table metrique_engagement

Métriques d'engagement communautaire (vues, téléchargements, citations, etc.)
"""
from sqlalchemy import Column, String, Integer, Date, CheckConstraint, Index, Enum
from sqlalchemy.orm import relationship

from .base import Base, UUIDMixin, TimestampMixin
from .enums import TypeMetriqueEnum


class MetriqueEngagement(Base, UUIDMixin, TimestampMixin):
    """
    Métrique d'engagement communautaire.
    
    Exemples : Vues, téléchargements, stars GitHub, citations, etc.
    
    Attributes:
        nom: Nom de la métrique
        description: Description de la métrique
        type_metrique: Type (views, downloads, citations, stars, etc.)
        source_metrique: Source de la métrique (ex: "arXiv", "GitHub")
        date_collecte: Date de collecte de la métrique
        valeur: Valeur numérique de la métrique
    """
    __tablename__ = "metrique_engagement"
    
    # Informations principales
    nom = Column(
        String(255),
        nullable=False,
        comment="Nom de la métrique"
    )
    description = Column(
        String(500),
        comment="Description de la métrique"
    )
    
    # Classification
    type_metrique = Column(Enum(TypeMetriqueEnum),
        nullable=False,
        comment="Type de métrique d'engagement"
    )
    
    # Métadonnées
    source_metrique = Column(
        String(255),
        comment="Source de la métrique (arXiv, GitHub, etc.)"
    )
    date_collecte = Column(
        Date,
        nullable=False,
        comment="Date de collecte de la métrique"
    )
    
    # Valeur
    valeur = Column(
        Integer,
        nullable=False,
        comment="Valeur numérique de la métrique"
    )
    
    # Contraintes
    __table_args__ = (
        CheckConstraint('valeur >= 0', name='check_metrique_valeur_positive'),
        Index('idx_metrique_type', 'type_metrique'),
        Index('idx_metrique_source', 'source_metrique'),
        Index('idx_metrique_date', 'date_collecte'),
    )
    
    # Relations
    publications = relationship(
        "PublicationMetrique",
        back_populates="metrique",
        lazy="select"
    )
    auteurs = relationship(
        "AuteurMetrique",
        back_populates="metrique",
        lazy="select"
    )
    
    def __repr__(self):
        return f"<MetriqueEngagement(id={self.id}, nom='{self.nom}', type='{self.type_metrique.value}', valeur={self.valeur})>"
