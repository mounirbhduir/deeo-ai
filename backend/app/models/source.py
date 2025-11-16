"""
Modèle SQLAlchemy pour la table source

Source des publications scientifiques (arXiv, IEEE, ACM, PubMed, etc.)
"""
from sqlalchemy import Column, String, Text, Integer, CheckConstraint
from sqlalchemy.orm import relationship

from .base import Base, UUIDMixin, TimestampMixin


class Source(Base, UUIDMixin, TimestampMixin):
    """
    Source de publication scientifique.
    
    Exemples : arXiv, IEEE, ACM, PubMed, Springer, Nature, etc.
    
    Attributes:
        nom: Nom de la source (ex: "arXiv", "IEEE Xplore")
        nom_court: Acronyme (ex: "arXiv", "IEEE")
        description: Description de la source
        url: URL du site web
        nombre_publications: Compteur de publications (calculé)
    """
    __tablename__ = "source"
    
    # Informations principales
    nom = Column(
        String(255),
        nullable=False,
        unique=True,
        comment="Nom de la source"
    )
    nom_court = Column(
        String(100),
        comment="Acronyme ou nom court"
    )
    description = Column(
        Text,
        comment="Description de la source"
    )
    url = Column(
        Text,
        comment="URL du site web de la source"
    )
    
    # Métriques (calculées par triggers)
    nombre_publications = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Nombre de publications de cette source"
    )
    
    # Contraintes
    __table_args__ = (
        CheckConstraint('nombre_publications >= 0', name='check_source_publications_positive'),
    )
    
    # Relations
    # publications = relationship(
    #     "Publication",
    #     back_populates="source_rel",
    #     lazy="select"
    # )
    
    def __repr__(self):
        return f"<Source(id={self.id}, nom='{self.nom}')>"
