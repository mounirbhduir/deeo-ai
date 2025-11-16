"""
Modèle SQLAlchemy pour la table organisation

Organisations (universités, entreprises, centres de recherche, think tanks)
"""
from sqlalchemy import Column, String, Integer, CheckConstraint, Index, Enum
from sqlalchemy.orm import relationship

from .base import Base, UUIDMixin, TimestampMixin
from .enums import TypeOrganisationEnum


class Organisation(Base, UUIDMixin, TimestampMixin):
    """
    Organisation impliquée dans la recherche IA.
    
    Exemples : MIT, Google DeepMind, Stanford, OpenAI, etc.
    
    Attributes:
        nom: Nom complet de l'organisation
        nom_court: Acronyme (ex: "MIT", "CNRS")
        type_organisation: Type (university, company, research_center, etc.)
        pays: Code pays ISO 3166-1 alpha-3 (ex: "USA", "FRA")
        ville: Ville
        secteur: Secteur d'activité
        url: Site web
        ranking_mondial: Classement mondial (si applicable)
        nombre_publications: Compteur de publications
        nombre_chercheurs: Compteur de chercheurs affiliés
    """
    __tablename__ = "organisation"
    
    # Informations principales
    nom = Column(
        String(255),
        nullable=False,
        comment="Nom complet de l'organisation"
    )
    nom_court = Column(
        String(100),
        comment="Acronyme ou nom court"
    )
    type_organisation = Column(Enum(TypeOrganisationEnum),
        nullable=False,
        comment="Type d'organisation"
    )
    
    # Localisation
    pays = Column(
        String(3),
        comment="Code pays ISO 3166-1 alpha-3"
    )
    ville = Column(
        String(255),
        comment="Ville"
    )
    
    # Détails
    secteur = Column(
        String(255),
        comment="Secteur d'activité"
    )
    url = Column(
        String(500),
        comment="URL du site web"
    )
    ranking_mondial = Column(
        Integer,
        comment="Classement mondial (si applicable)"
    )
    
    # Métriques (calculées par triggers)
    nombre_publications = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Nombre de publications associées"
    )
    nombre_chercheurs = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Nombre de chercheurs affiliés"
    )
    
    # Contraintes
    __table_args__ = (
        CheckConstraint('nombre_publications >= 0', name='check_org_publications_positive'),
        CheckConstraint('nombre_chercheurs >= 0', name='check_org_chercheurs_positive'),
        CheckConstraint('ranking_mondial > 0', name='check_org_ranking_positive'),
        Index('idx_organisation_nom', 'nom'),
        Index('idx_organisation_type', 'type_organisation'),
        Index('idx_organisation_pays', 'pays'),
        Index('idx_organisation_ranking', 'ranking_mondial'),
    )
    
    # Relations
    affiliations = relationship(
        "Affiliation",
        back_populates="organisation",
        lazy="select"
    )
    evenements_organises = relationship(
        "Evenement",
        back_populates="organisation_principale",
        lazy="select"
    )
    datasets_crees = relationship(
        "Dataset",
        back_populates="organisation_creatrice",
        lazy="select"
    )
    collaborations = relationship(
        "Collaboration",
        back_populates="organisation_principale",
        lazy="select"
    )
    
    def __repr__(self):
        return f"<Organisation(id={self.id}, nom='{self.nom}', type='{self.type_organisation.value}')>"
