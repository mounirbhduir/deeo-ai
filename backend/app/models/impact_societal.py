"""
Modèle SQLAlchemy pour la table impact_societal

Évaluation des impacts sociétaux de l'IA
"""
from sqlalchemy import Column, String, Text, Date, Index, Enum
from sqlalchemy.orm import relationship

from .base import Base, UUIDMixin, TimestampMixin
from .enums import TypeImpactEnum, NiveauImpactEnum


class ImpactSocietal(Base, UUIDMixin, TimestampMixin):
    """
    Impact sociétal d'une technologie ou recherche IA.
    
    Exemples : Impact sur l'emploi, la santé, l'éducation, l'environnement, etc.
    
    Attributes:
        titre: Titre de l'impact identifié
        description: Description détaillée
        type_impact: Type (social, economic, environmental, ethical, etc.)
        niveau_impact: Niveau (low, medium, high, critical)
        domaine: Domaine d'application
        date_identification: Date d'identification de l'impact
        source: Source de l'analyse
    """
    __tablename__ = "impact_societal"
    
    # Informations principales
    titre = Column(
        String(500),
        nullable=False,
        comment="Titre de l'impact identifié"
    )
    description = Column(
        Text,
        comment="Description détaillée de l'impact"
    )
    
    # Classification
    type_impact = Column(Enum(TypeImpactEnum),
        nullable=False,
        comment="Type d'impact sociétal"
    )
    niveau_impact = Column(Enum(NiveauImpactEnum),
        nullable=False,
        comment="Niveau de gravité/importance de l'impact"
    )
    
    # Métadonnées
    domaine = Column(
        String(255),
        comment="Domaine d'application (santé, finance, etc.)"
    )
    date_identification = Column(
        Date,
        comment="Date d'identification de l'impact"
    )
    source = Column(
        String(500),
        comment="Source de l'analyse d'impact"
    )
    
    # Contraintes
    __table_args__ = (
        Index('idx_impact_type', 'type_impact'),
        Index('idx_impact_niveau', 'niveau_impact'),
        Index('idx_impact_domaine', 'domaine'),
    )
    
    # Relations
    publications = relationship(
        "PublicationImpact",
        back_populates="impact",
        lazy="select"
    )
    
    def __repr__(self):
        return f"<ImpactSocietal(id={self.id}, titre='{self.titre[:50]}...', type='{self.type_impact.value}')>"
