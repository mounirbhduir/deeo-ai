"""
Modèle SQLAlchemy pour la table publication

Publications scientifiques (hub central du système DEEO.AI)
"""
from sqlalchemy import Column, String, Text, Date, Integer, Numeric, CheckConstraint, ForeignKey, Index, Enum
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR
from sqlalchemy.orm import relationship

from .base import Base, UUIDMixin, TimestampMixin
from .enums import TypePublicationEnum, StatusPublicationEnum


class Publication(Base, UUIDMixin, TimestampMixin):
    """
    Publication scientifique en IA (hub central du modèle).
    
    Attributes:
        titre: Titre de la publication
        abstract: Résumé/Abstract
        doi: Digital Object Identifier (CRITIQUE Phase 3 - Semantic Scholar)
        arxiv_id: Identifiant arXiv (CRITIQUE Phase 3 - alternative au DOI)
        url: URL de la publication
        date_publication: Date de publication
        type_publication: Type (article, preprint, conference_paper, etc.)
        status: Statut d'enrichissement (Phase 3 - pipeline Semantic Scholar)
        language: Langue (code ISO 639-1)
        source_nom: Nom de la source (arXiv, IEEE, etc.)
        evenement_id: ID de l'événement (si conference paper)
        nombre_citations: Nombre de citations (Phase 3 - enrichissement)
        nombre_auteurs: Nombre d'auteurs
        score_popularite: Score de popularité calculé
        search_vector: Vecteur pour full-text search (colonne générée)
    """
    __tablename__ = "publication"
    
    # Informations principales
    titre = Column(
        String(500),
        nullable=False,
        comment="Titre de la publication"
    )
    abstract = Column(
        Text,
        comment="Résumé/Abstract"
    )
    
    # Identifiants externes (CRITIQUES PHASE 3)
    doi = Column(
        String(255),
        unique=True,
        comment="Digital Object Identifier (CRITIQUE pour Semantic Scholar Phase 3)"
    )
    arxiv_id = Column(
        String(50),
        comment="Identifiant arXiv (CRITIQUE Phase 3 - alternative au DOI)"
    )
    url = Column(
        String(500),
        comment="URL de la publication"
    )
    
    # Métadonnées
    date_publication = Column(
        Date,
        nullable=False,
        comment="Date de publication"
    )
    type_publication = Column(Enum(TypePublicationEnum),
        nullable=False,
        comment="Type de publication"
    )
    status = Column(Enum(StatusPublicationEnum),
        nullable=False,
        default=StatusPublicationEnum.PUBLISHED,
        comment="Statut d'enrichissement (Phase 3 - pipeline)"
    )
    language = Column(
        String(10),
        default='en',
        comment="Code langue ISO 639-1"
    )
    
    # Source et événement
    source_nom = Column(
        String(100),
        comment="Nom de la source (arXiv, IEEE, ACM, etc.)"
    )
    evenement_id = Column(
        UUID(as_uuid=True),
        ForeignKey('evenement.id', ondelete='SET NULL'),
        nullable=True,
        comment="Événement associé (si conference/workshop paper)"
    )
    
    # Métriques (calculées par triggers et enrichissement Phase 3)
    nombre_citations = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Nombre de citations (Phase 3 - Semantic Scholar)"
    )
    nombre_auteurs = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Nombre d'auteurs"
    )
    score_popularite = Column(
        Numeric(5, 2),
        default=0.0,
        nullable=False,
        comment="Score de popularité calculé"
    )
    
    # Full-text search (colonne générée - pas besoin de GENERATED ALWAYS dans SQLAlchemy)
    search_vector = Column(
        TSVECTOR,
        comment="Vecteur pour full-text search (généré automatiquement)"
    )
    
    # Contraintes
    __table_args__ = (
        CheckConstraint('nombre_citations >= 0', name='check_publication_citations_positive'),
        CheckConstraint('nombre_auteurs >= 0', name='check_publication_auteurs_positive'),
        CheckConstraint('score_popularite >= 0', name='check_publication_score_positive'),
        Index('idx_publication_doi', 'doi', unique=True, postgresql_where='doi IS NOT NULL'),
        Index('idx_publication_arxiv_id', 'arxiv_id', postgresql_where='arxiv_id IS NOT NULL'),
        Index('idx_publication_date', 'date_publication', postgresql_ops={'date_publication': 'DESC'}),
        Index('idx_publication_type', 'type_publication'),
        Index('idx_publication_status', 'status'),
        Index('idx_publication_citations', 'nombre_citations', postgresql_ops={'nombre_citations': 'DESC'}),
        Index('idx_publication_search', 'search_vector', postgresql_using='gin'),
        Index('idx_publication_source', 'source_nom'),
    )
    
    # Relations
    evenement = relationship(
        "Evenement",
        back_populates="publications",
        lazy="select"
    )
    auteurs = relationship(
        "PublicationAuteur",
        back_populates="publication",
        lazy="select"
    )
    themes = relationship(
        "PublicationTheme",
        back_populates="publication",
        lazy="select"
    )
    technologies = relationship(
        "PublicationTechnologie",
        back_populates="publication",
        lazy="select"
    )
    datasets = relationship(
        "PublicationDataset",
        back_populates="publication",
        lazy="select"
    )
    outils = relationship(
        "PublicationOutil",
        back_populates="publication",
        lazy="select"
    )
    citations_sources = relationship(
        "Citation",
        foreign_keys="Citation.publication_source_id",
        back_populates="publication_source",
        lazy="select"
    )
    citations_cibles = relationship(
        "Citation",
        foreign_keys="Citation.publication_cible_id",
        back_populates="publication_cible",
        lazy="select"
    )
    impacts = relationship(
        "PublicationImpact",
        back_populates="publication",
        lazy="select"
    )
    metriques = relationship(
        "PublicationMetrique",
        back_populates="publication",
        lazy="select"
    )
    
    def __repr__(self):
        return f"<Publication(id={self.id}, titre='{self.titre[:50]}...', status='{self.status.value}')>"
