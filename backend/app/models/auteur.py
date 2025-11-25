"""
Modèle SQLAlchemy pour la table auteur

Auteurs/chercheurs en IA
"""
from sqlalchemy import Column, String, Integer, CheckConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy

from .base import Base, UUIDMixin, TimestampMixin


class Auteur(Base, UUIDMixin, TimestampMixin):
    """
    Auteur/chercheur en intelligence artificielle.
    
    Attributes:
        nom: Nom de famille
        prenom: Prénom
        email: Email (si disponible)
        orcid: Identifiant ORCID (format XXXX-XXXX-XXXX-XXXX)
        google_scholar_id: ID Google Scholar
        semantic_scholar_id: ID Semantic Scholar (Phase 3 - enrichissement)
        homepage_url: Page personnelle
        h_index: H-index (Phase 3 - calculé via Semantic Scholar)
        nombre_publications: Compteur de publications
        nombre_citations: Compteur total de citations
    """
    __tablename__ = "auteur"
    
    # Informations personnelles
    nom = Column(
        String(255),
        nullable=False,
        comment="Nom de famille"
    )
    prenom = Column(
        String(255),
        comment="Prénom"
    )
    email = Column(
        String(255),
        comment="Email de contact"
    )
    
    # Identifiants externes
    orcid = Column(
        String(19),
        unique=True,
        comment="Identifiant ORCID (XXXX-XXXX-XXXX-XXXX)"
    )
    google_scholar_id = Column(
        String(50),
        comment="Identifiant Google Scholar"
    )
    semantic_scholar_id = Column(
        String(50),
        comment="Identifiant Semantic Scholar (Phase 3 enrichissement)"
    )
    homepage_url = Column(
        String(500),
        comment="URL de la page personnelle"
    )
    
    # Métriques (calculées par triggers et enrichissement Phase 3)
    h_index = Column(
        Integer,
        default=0,
        nullable=False,
        comment="H-index (calculé via Semantic Scholar en Phase 3)"
    )
    nombre_publications = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Nombre de publications"
    )
    nombre_citations = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Nombre total de citations"
    )
    
    # Contraintes
    __table_args__ = (
        CheckConstraint('h_index >= 0', name='check_auteur_h_index_positive'),
        CheckConstraint('nombre_publications >= 0', name='check_auteur_publications_positive'),
        CheckConstraint('nombre_citations >= 0', name='check_auteur_citations_positive'),
        Index('idx_auteur_nom_prenom', 'nom', 'prenom'),
        Index('idx_auteur_orcid', 'orcid', unique=True, postgresql_where='orcid IS NOT NULL'),
        Index('idx_auteur_h_index', 'h_index', postgresql_ops={'h_index': 'DESC'}),
        Index('idx_auteur_semantic_scholar', 'semantic_scholar_id'),
    )
    
    # Relations
    # Association object relationship (for when we need ordre, role)
    publications = relationship(
        "PublicationAuteur",
        back_populates="auteur",
        lazy="select",
        order_by="PublicationAuteur.ordre"
    )

    # Direct many-to-many access to Publication objects (bypassing association)
    publications_list = association_proxy(
        "publications",
        "publication",
        creator=lambda pub: __import__('app.models.publication_auteur', fromlist=['PublicationAuteur']).PublicationAuteur(publication=pub)
    )

    affiliations = relationship(
        "Affiliation",
        back_populates="auteur",
        lazy="select"
    )
    collaborations = relationship(
        "CollaborationAuteur",
        back_populates="auteur",
        lazy="select"
    )
    
    def __repr__(self):
        return f"<Auteur(id={self.id}, nom='{self.nom}', prenom='{self.prenom}', h_index={self.h_index})>"
