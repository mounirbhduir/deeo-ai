"""
Modèle SQLAlchemy pour la table evenement

Événements scientifiques (conférences, workshops, symposiums, etc.)
"""
from sqlalchemy import Column, String, Text, Date, Integer, CheckConstraint, ForeignKey, Index, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, UUIDMixin, TimestampMixin
from .enums import TypeEvenementEnum, StatutEvenementEnum


class Evenement(Base, UUIDMixin, TimestampMixin):
    """
    Événement scientifique lié à l'IA.
    
    Exemples : NeurIPS, ICML, CVPR, ICLR, ACL, etc.
    
    Attributes:
        nom: Nom de l'événement (ex: "NeurIPS 2024")
        nom_complet: Nom complet
        type_evenement: Type (conference, workshop, symposium, etc.)
        statut: Statut actuel (planned, ongoing, completed, cancelled)
        date_debut: Date de début
        date_fin: Date de fin
        lieu: Lieu physique
        ville: Ville
        pays: Code pays ISO 3166-1 alpha-3
        url: Site web de l'événement
        organisation_principale_id: Organisation organisatrice principale
        nombre_participants: Nombre de participants
        nombre_publications: Nombre de publications associées
    """
    __tablename__ = "evenement"
    
    # Informations principales
    nom = Column(
        String(255),
        nullable=False,
        comment="Nom de l'événement"
    )
    nom_complet = Column(
        String(500),
        comment="Nom complet de l'événement"
    )
    type_evenement = Column(Enum(TypeEvenementEnum),
        nullable=False,
        comment="Type d'événement"
    )
    statut = Column(Enum(StatutEvenementEnum),
        nullable=False,
        default=StatutEvenementEnum.PLANNED,
        comment="Statut actuel de l'événement"
    )
    
    # Dates
    date_debut = Column(
        Date,
        nullable=False,
        comment="Date de début"
    )
    date_fin = Column(
        Date,
        comment="Date de fin"
    )
    
    # Localisation
    lieu = Column(
        String(500),
        comment="Lieu physique de l'événement"
    )
    ville = Column(
        String(255),
        comment="Ville"
    )
    pays = Column(
        String(3),
        comment="Code pays ISO 3166-1 alpha-3"
    )
    
    # Détails
    url = Column(
        String(500),
        comment="URL du site web de l'événement"
    )
    description = Column(
        Text,
        comment="Description de l'événement"
    )
    
    # Organisation principale
    organisation_principale_id = Column(
        UUID(as_uuid=True),
        ForeignKey('organisation.id', ondelete='SET NULL'),
        nullable=True,
        comment="Organisation organisatrice principale"
    )
    
    # Métriques
    nombre_participants = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Nombre de participants"
    )
    nombre_publications = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Nombre de publications présentées"
    )
    
    # Contraintes
    __table_args__ = (
        CheckConstraint('date_fin IS NULL OR date_fin >= date_debut', 
                       name='check_evenement_dates_valid'),
        CheckConstraint('nombre_participants >= 0', 
                       name='check_evenement_participants_positive'),
        CheckConstraint('nombre_publications >= 0', 
                       name='check_evenement_publications_positive'),
        Index('idx_evenement_date_debut', 'date_debut'),
        Index('idx_evenement_type', 'type_evenement'),
        Index('idx_evenement_statut', 'statut'),
    )
    
    # Relations
    organisation_principale = relationship(
        "Organisation",
        back_populates="evenements_organises",
        lazy="select"
    )
    publications = relationship(
        "Publication",
        back_populates="evenement",
        lazy="select"
    )
    
    def __repr__(self):
        return f"<Evenement(id={self.id}, nom='{self.nom}', type='{self.type_evenement.value}')>"
