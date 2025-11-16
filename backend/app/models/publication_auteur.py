"""
Table d'association publication_auteur

Relation N-N entre Publication et Auteur avec ordre et rôle
"""
from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class PublicationAuteur(Base, TimestampMixin):
    """
    Association entre Publication et Auteur (ordre des auteurs important).
    
    Attributes:
        publication_id: ID de la publication
        auteur_id: ID de l'auteur
        ordre: Position dans la liste d'auteurs (1 = premier auteur)
        role: Rôle spécifique (ex: "first_author", "corresponding_author")
    """
    __tablename__ = "publication_auteur"
    
    # Clés étrangères
    publication_id = Column(
        UUID(as_uuid=True),
        ForeignKey('publication.id', ondelete='CASCADE'),
        primary_key=True,
        comment="ID de la publication"
    )
    auteur_id = Column(
        UUID(as_uuid=True),
        ForeignKey('auteur.id', ondelete='RESTRICT'),
        primary_key=True,
        comment="ID de l'auteur"
    )
    
    # Métadonnées
    ordre = Column(
        Integer,
        nullable=False,
        comment="Position dans la liste d'auteurs (1 = premier)"
    )
    role = Column(
        String(50),
        comment="Rôle de l'auteur (first_author, corresponding_author, etc.)"
    )
    
    # Contraintes
    __table_args__ = (
        CheckConstraint('ordre > 0', name='check_publication_auteur_ordre_positive'),
        UniqueConstraint('publication_id', 'ordre', name='uq_publication_auteur_ordre'),
        Index('idx_publication_auteur_publication', 'publication_id'),
        Index('idx_publication_auteur_auteur', 'auteur_id'),
    )
    
    # Relations
    publication = relationship(
        "Publication",
        back_populates="auteurs",
        lazy="select"
    )
    auteur = relationship(
        "Auteur",
        back_populates="publications",
        lazy="select"
    )
    
    def __repr__(self):
        return f"<PublicationAuteur(publication_id={self.publication_id}, auteur_id={self.auteur_id}, ordre={self.ordre})>"
