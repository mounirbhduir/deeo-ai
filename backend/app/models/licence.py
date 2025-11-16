"""
Modèle SQLAlchemy pour la table licence

Licences logicielles pour datasets et outils (MIT, Apache, GPL, etc.)
"""
from sqlalchemy import Column, String, Text, Boolean, Enum
from sqlalchemy.orm import relationship

from .base import Base, UUIDMixin, TimestampMixin
from .enums import TypeLicenceEnum


class Licence(Base, UUIDMixin, TimestampMixin):
    """
    Licence logicielle pour datasets et outils.
    
    Exemples : MIT, Apache 2.0, GPL v3, BSD, Creative Commons, etc.
    
    Attributes:
        nom: Nom de la licence (ex: "MIT License")
        type_licence: Type de licence (ENUM)
        description: Description de la licence
        url: URL vers le texte complet
        is_open_source: Indicateur open source
    """
    __tablename__ = "licence"
    
    # Informations principales
    nom = Column(
        String(255),
        nullable=False,
        unique=True,
        comment="Nom de la licence"
    )
    type_licence = Column(Enum(TypeLicenceEnum),
        nullable=False,
        comment="Type de licence"
    )
    description = Column(
        Text,
        comment="Description de la licence"
    )
    url = Column(
        Text,
        comment="URL vers le texte complet de la licence"
    )
    
    # Propriétés
    is_open_source = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Indique si la licence est open source"
    )
    
    # Relations
    datasets = relationship(
        "Dataset",
        back_populates="licence_rel",
        lazy="select"
    )
    outils = relationship(
        "Outil",
        back_populates="licence_rel",
        lazy="select"
    )
    
    def __repr__(self):
        return f"<Licence(id={self.id}, nom='{self.nom}', type='{self.type_licence.value}')>"
