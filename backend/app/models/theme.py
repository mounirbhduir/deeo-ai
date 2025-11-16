"""
Modèle SQLAlchemy pour la table theme

Thèmes de recherche IA organisés en hiérarchie taxonomique (ontologie)
"""
from sqlalchemy import Column, String, Text, Integer, CheckConstraint, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, UUIDMixin, TimestampMixin


class Theme(Base, UUIDMixin, TimestampMixin):
    """
    Thème de recherche en IA, organisé en hiérarchie taxonomique.
    
    Basé sur l'ontologie DEEO.AI (JSON-LD).
    
    Exemples :
    - Niveau 1 : Machine Learning, NLP, Computer Vision
    - Niveau 2 : Deep Learning, Reinforcement Learning
    - Niveau 3 : CNN, RNN, Transformers
    
    Attributes:
        label: Nom du thème (ex: "Machine Learning")
        description: Description du thème
        niveau_hierarchie: Profondeur dans l'arbre (0 = racine)
        parent_id: ID du thème parent (NULL = racine)
        chemin_hierarchie: Chemin complet (ex: "AI/ML/Deep Learning")
        nombre_publications: Compteur de publications (calculé)
    """
    __tablename__ = "theme"
    
    # Informations principales
    label = Column(
        String(255),
        nullable=False,
        comment="Nom du thème"
    )
    description = Column(
        Text,
        comment="Description du thème"
    )
    
    # Hiérarchie
    niveau_hierarchie = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Profondeur dans l'arbre (0 = racine)"
    )
    parent_id = Column(
        UUID(as_uuid=True),
        ForeignKey('theme.id', ondelete='RESTRICT'),
        nullable=True,
        comment="ID du thème parent"
    )
    chemin_hierarchie = Column(
        Text,
        comment="Chemin complet (ex: 'AI/ML/Deep Learning')"
    )
    
    # Métriques (calculées par triggers)
    nombre_publications = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Nombre de publications associées"
    )
    
    # Contraintes
    __table_args__ = (
        CheckConstraint('nombre_publications >= 0', name='check_theme_publications_positive'),
        CheckConstraint('niveau_hierarchie >= 0 AND niveau_hierarchie <= 10', 
                       name='check_theme_niveau_valid'),
        Index('idx_theme_parent_id', 'parent_id'),
        Index('idx_theme_niveau', 'niveau_hierarchie'),
        Index('idx_theme_label', 'label'),
        # Index GIN pour recherche textuelle sur chemin
        Index('idx_theme_chemin', 'chemin_hierarchie', postgresql_using='gin',
              postgresql_ops={'chemin_hierarchie': 'gin_trgm_ops'}),
    )
    
    # Relations
    # Auto-référence pour la hiérarchie
    parent = relationship(
        "Theme",
        remote_side="Theme.id",
        back_populates="enfants",
        lazy="select"
    )
    enfants = relationship(
        "Theme",
        back_populates="parent",
        lazy="select"
    )
    
    # Relations N-N
    publications = relationship(
        "PublicationTheme",
        back_populates="theme",
        lazy="select"
    )
    technologies = relationship(
        "Technologie",
        back_populates="theme_rel",
        lazy="select"
    )
    
    def __repr__(self):
        return f"<Theme(id={self.id}, label='{self.label}', niveau={self.niveau_hierarchie})>"
