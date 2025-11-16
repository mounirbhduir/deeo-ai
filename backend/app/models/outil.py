"""
Modèle SQLAlchemy pour la table outil

Outils logiciels pour développement/déploiement IA
"""
from sqlalchemy import Column, String, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, UUIDMixin, TimestampMixin


class Outil(Base, UUIDMixin, TimestampMixin):
    """
    Outil logiciel pour développement/déploiement IA.
    
    Exemples : Jupyter, Docker, Kubernetes, MLflow, Weights & Biases, etc.
    
    Attributes:
        nom: Nom de l'outil (ex: "Jupyter Notebook", "MLflow")
        description: Description de l'outil
        url: Site web officiel
        github_url: Repository GitHub
        licence_id: Licence de l'outil
    """
    __tablename__ = "outil"
    
    # Informations principales
    nom = Column(
        String(255),
        nullable=False,
        comment="Nom de l'outil"
    )
    description = Column(
        Text,
        comment="Description de l'outil"
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
    
    # Licence
    licence_id = Column(
        UUID(as_uuid=True),
        ForeignKey('licence.id', ondelete='SET NULL'),
        nullable=True,
        comment="Licence de l'outil"
    )
    
    # Contraintes
    __table_args__ = (
        Index('idx_outil_nom', 'nom'),
        Index('idx_outil_licence', 'licence_id'),
    )
    
    # Relations
    licence_rel = relationship(
        "Licence",
        back_populates="outils",
        lazy="select"
    )
    publications = relationship(
        "PublicationOutil",
        back_populates="outil",
        lazy="select"
    )
    technologies_associees = relationship(
        "TechnologieOutil",
        back_populates="outil",
        lazy="select"
    )
    
    def __repr__(self):
        return f"<Outil(id={self.id}, nom='{self.nom}')>"
