"""
Modèle SQLAlchemy pour la table technologie

Technologies IA (algorithmes, frameworks, architectures, bibliothèques)
"""
from sqlalchemy import Column, String, Text, Numeric, ForeignKey, Index, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, UUIDMixin, TimestampMixin
from .enums import TypeTechnologieEnum, NiveauMaturiteEnum


class Technologie(Base, UUIDMixin, TimestampMixin):
    """
    Technologie IA (algorithme, framework, architecture, bibliothèque).
    
    Exemples : TensorFlow, PyTorch, BERT, ResNet, Adam optimizer, etc.
    
    Attributes:
        nom: Nom de la technologie (ex: "TensorFlow", "BERT")
        description: Description de la technologie
        type_technologie: Type (algorithm, framework, architecture, etc.)
        theme_id: Thème associé (ex: Deep Learning)
        niveau_maturite: Niveau de maturité (research, prototype, production, etc.)
        popularite: Score de popularité
        url: Site web officiel
        github_url: Repository GitHub
    """
    __tablename__ = "technologie"
    
    # Informations principales
    nom = Column(
        String(255),
        nullable=False,
        comment="Nom de la technologie"
    )
    description = Column(
        Text,
        comment="Description de la technologie"
    )
    type_technologie = Column(Enum(TypeTechnologieEnum),
        nullable=False,
        comment="Type de technologie"
    )
    
    # Relation avec thème
    theme_id = Column(
        UUID(as_uuid=True),
        ForeignKey('theme.id', ondelete='RESTRICT'),
        nullable=False,
        comment="Thème de recherche associé"
    )
    
    # Métadonnées
    niveau_maturite = Column(Enum(NiveauMaturiteEnum),
        comment="Niveau de maturité technologique"
    )
    popularite = Column(
        Numeric(5, 2),
        default=0.0,
        comment="Score de popularité"
    )
    
    # Liens
    url = Column(
        String(500),
        comment="URL du site web officiel"
    )
    github_url = Column(
        String(500),
        comment="URL du repository GitHub"
    )
    
    # Contraintes
    __table_args__ = (
        Index('idx_technologie_nom', 'nom'),
        Index('idx_technologie_type', 'type_technologie'),
        Index('idx_technologie_theme', 'theme_id'),
        Index('idx_technologie_maturite', 'niveau_maturite'),
    )
    
    # Relations
    theme_rel = relationship(
        "Theme",
        back_populates="technologies",
        lazy="select"
    )
    publications = relationship(
        "PublicationTechnologie",
        back_populates="technologie",
        lazy="select"
    )
    datasets_associes = relationship(
        "TechnologieDataset",
        back_populates="technologie",
        lazy="select"
    )
    outils_associes = relationship(
        "TechnologieOutil",
        back_populates="technologie",
        lazy="select"
    )
    
    def __repr__(self):
        return f"<Technologie(id={self.id}, nom='{self.nom}', type='{self.type_technologie.value}')>"
