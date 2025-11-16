"""
Modèle SQLAlchemy pour la table dataset

Jeux de données utilisés en IA/ML
"""
from sqlalchemy import Column, String, Text, Date, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, UUIDMixin, TimestampMixin


class Dataset(Base, UUIDMixin, TimestampMixin):
    """
    Jeu de données pour l'entraînement/évaluation de modèles IA.
    
    Exemples : ImageNet, COCO, MNIST, Wikipedia, Common Crawl, etc.
    
    Attributes:
        nom: Nom du dataset (ex: "ImageNet", "COCO")
        description: Description du dataset
        url: URL de téléchargement ou documentation
        taille: Taille du dataset (ex: "10GB", "1M samples")
        format: Format des données (CSV, JSON, HDF5, etc.)
        licence_id: Licence du dataset
        organisation_id: Organisation créatrice
        date_creation: Date de création du dataset
    """
    __tablename__ = "dataset"
    
    # Informations principales
    nom = Column(
        String(255),
        nullable=False,
        comment="Nom du dataset"
    )
    description = Column(
        Text,
        comment="Description du dataset"
    )
    url = Column(
        String(500),
        comment="URL de téléchargement ou documentation"
    )
    
    # Caractéristiques
    taille = Column(
        String(50),
        comment="Taille du dataset (ex: '10GB', '1M samples')"
    )
    format = Column(
        String(100),
        comment="Format des données (CSV, JSON, HDF5, etc.)"
    )
    
    # Relations
    licence_id = Column(
        UUID(as_uuid=True),
        ForeignKey('licence.id', ondelete='SET NULL'),
        nullable=True,
        comment="Licence du dataset"
    )
    organisation_id = Column(
        UUID(as_uuid=True),
        ForeignKey('organisation.id', ondelete='SET NULL'),
        nullable=True,
        comment="Organisation créatrice"
    )
    
    # Métadonnées
    date_creation = Column(
        Date,
        comment="Date de création du dataset"
    )
    
    # Contraintes
    __table_args__ = (
        Index('idx_dataset_nom', 'nom'),
        Index('idx_dataset_licence', 'licence_id'),
        Index('idx_dataset_organisation', 'organisation_id'),
    )
    
    # Relations
    licence_rel = relationship(
        "Licence",
        back_populates="datasets",
        lazy="select"
    )
    organisation_creatrice = relationship(
        "Organisation",
        back_populates="datasets_crees",
        lazy="select"
    )
    publications = relationship(
        "PublicationDataset",
        back_populates="dataset",
        lazy="select"
    )
    technologies_associees = relationship(
        "TechnologieDataset",
        back_populates="dataset",
        lazy="select"
    )
    
    def __repr__(self):
        return f"<Dataset(id={self.id}, nom='{self.nom}')>"
