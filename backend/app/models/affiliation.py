"""
Table d'association affiliation (relation temporelle Auteur-Organisation)
"""
from sqlalchemy import Column, String, Date, ForeignKey, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


class Affiliation(Base, TimestampMixin):
    """
    Affiliation temporelle entre Auteur et Organisation.
    
    Attributes:
        auteur_id: ID de l'auteur
        organisation_id: ID de l'organisation
        date_debut: Date de début de l'affiliation
        date_fin: Date de fin (NULL = toujours en poste)
        poste: Poste occupé (ex: "Professor", "Research Scientist")
    """
    __tablename__ = "affiliation"
    
    auteur_id = Column(
        UUID(as_uuid=True),
        ForeignKey('auteur.id', ondelete='CASCADE'),
        primary_key=True
    )
    organisation_id = Column(
        UUID(as_uuid=True),
        ForeignKey('organisation.id', ondelete='RESTRICT'),
        primary_key=True
    )
    date_debut = Column(
        Date,
        primary_key=True,
        nullable=False,
        comment="Date de début de l'affiliation"
    )
    
    date_fin = Column(
        Date,
        comment="Date de fin (NULL = toujours en poste)"
    )
    poste = Column(
        String(255),
        comment="Poste occupé"
    )
    
    __table_args__ = (
        CheckConstraint('date_fin IS NULL OR date_fin >= date_debut',
                       name='check_affiliation_dates_valid'),
        Index('idx_affiliation_auteur', 'auteur_id'),
        Index('idx_affiliation_organisation', 'organisation_id'),
        Index('idx_affiliation_dates', 'date_debut', 'date_fin'),
        Index('idx_affiliation_active', 'auteur_id', postgresql_where='date_fin IS NULL'),
    )
    
    auteur = relationship("Auteur", back_populates="affiliations", lazy="select")
    organisation = relationship("Organisation", back_populates="affiliations", lazy="select")
