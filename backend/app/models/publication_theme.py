"""
Table d'association publication_theme

Relation N-N entre Publication et Theme avec score de pertinence
"""
from sqlalchemy import Column, Numeric, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class PublicationTheme(Base, TimestampMixin):
    """
    Association entre Publication et Theme avec score de pertinence.
    
    Le score de pertinence est calculé par le classificateur ML (Phase 3).
    
    Attributes:
        publication_id: ID de la publication
        theme_id: ID du thème
        pertinence: Score de pertinence (0.0 à 1.0)
    """
    __tablename__ = "publication_theme"
    
    # Clés étrangères
    publication_id = Column(
        UUID(as_uuid=True),
        ForeignKey('publication.id', ondelete='CASCADE'),
        primary_key=True,
        comment="ID de la publication"
    )
    theme_id = Column(
        UUID(as_uuid=True),
        ForeignKey('theme.id', ondelete='CASCADE'),
        primary_key=True,
        comment="ID du thème"
    )
    
    # Score de pertinence (Phase 3 - classificateur ML)
    pertinence = Column(
        Numeric(3, 2),
        default=1.0,
        nullable=False,
        comment="Score de pertinence (0.0 à 1.0, calculé par ML Phase 3)"
    )
    
    # Contraintes
    __table_args__ = (
        CheckConstraint('pertinence >= 0 AND pertinence <= 1', 
                       name='check_publication_theme_pertinence_valid'),
        Index('idx_publication_theme_publication', 'publication_id'),
        Index('idx_publication_theme_theme', 'theme_id'),
        Index('idx_publication_theme_pertinence', 'pertinence', 
              postgresql_ops={'pertinence': 'DESC'}),
    )
    
    # Relations
    publication = relationship(
        "Publication",
        back_populates="themes",
        lazy="select"
    )
    theme = relationship(
        "Theme",
        back_populates="publications",
        lazy="select"
    )
    
    def __repr__(self):
        return f"<PublicationTheme(publication_id={self.publication_id}, theme_id={self.theme_id}, pertinence={self.pertinence})>"
