"""
Types énumérés (ENUM) pour les modèles DEEO.AI

Ce module définit tous les types ENUM PostgreSQL utilisés dans la base de données.
"""
import enum


class TypeOrganisationEnum(str, enum.Enum):
    """Type d'organisation"""
    UNIVERSITY = "university"
    COMPANY = "company"
    RESEARCH_CENTER = "research_center"
    THINK_TANK = "think_tank"
    GOVERNMENT = "government"
    NGO = "ngo"
    OTHER = "other"


class TypePublicationEnum(str, enum.Enum):
    """Type de publication scientifique"""
    ARTICLE = "article"
    PREPRINT = "preprint"
    CONFERENCE_PAPER = "conference_paper"
    JOURNAL_PAPER = "journal_paper"
    TUTORIAL = "tutorial"
    SURVEY = "survey"
    WORKSHOP_PAPER = "workshop_paper"
    THESIS = "thesis"
    BOOK_CHAPTER = "book_chapter"
    TECHNICAL_REPORT = "technical_report"
    OTHER = "other"


class TypeTechnologieEnum(str, enum.Enum):
    """Type de technologie IA"""
    ALGORITHM = "algorithm"
    FRAMEWORK = "framework"
    ARCHITECTURE = "architecture"
    TECHNIQUE = "technique"
    TOOL = "tool"
    LIBRARY = "library"
    PLATFORM = "platform"


class NiveauMaturiteEnum(str, enum.Enum):
    """Niveau de maturité technologique"""
    RESEARCH = "research"
    PROTOTYPE = "prototype"
    PRODUCTION = "production"
    MATURE = "mature"
    DEPRECATED = "deprecated"


class TypeLicenceEnum(str, enum.Enum):
    """Type de licence logicielle"""
    OPEN_SOURCE = "open_source"
    PROPRIETARY = "proprietary"
    CREATIVE_COMMONS = "creative_commons"
    MIT = "mit"
    APACHE = "apache"
    GPL = "gpl"
    BSD = "bsd"
    OTHER = "other"


class TypeEvenementEnum(str, enum.Enum):
    """Type d'événement scientifique"""
    CONFERENCE = "conference"
    WORKSHOP = "workshop"
    SYMPOSIUM = "symposium"
    SEMINAR = "seminar"
    WEBINAR = "webinar"
    HACKATHON = "hackathon"
    COMPETITION = "competition"
    OTHER = "other"


class StatutEvenementEnum(str, enum.Enum):
    """Statut d'un événement"""
    PLANNED = "planned"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TypeImpactEnum(str, enum.Enum):
    """Type d'impact sociétal"""
    SOCIAL = "social"
    ECONOMIC = "economic"
    ENVIRONMENTAL = "environmental"
    ETHICAL = "ethical"
    POLITICAL = "political"
    HEALTH = "health"
    EDUCATION = "education"
    OTHER = "other"


class NiveauImpactEnum(str, enum.Enum):
    """Niveau d'impact sociétal"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TypeMetriqueEnum(str, enum.Enum):
    """Type de métrique d'engagement"""
    VIEWS = "views"
    DOWNLOADS = "downloads"
    CITATIONS = "citations"
    STARS = "stars"
    FORKS = "forks"
    MENTIONS = "mentions"
    SHARES = "shares"
    OTHER = "other"


class TypeCollaborationEnum(str, enum.Enum):
    """Type de collaboration"""
    RESEARCH = "research"
    INDUSTRIAL = "industrial"
    ACADEMIC = "academic"
    INTERNATIONAL = "international"
    PUBLIC_PRIVATE = "public_private"
    OTHER = "other"


class StatusPublicationEnum(str, enum.Enum):
    """
    Statut d'enrichissement d'une publication (Phase 3).
    
    Utilisé par le pipeline d'enrichissement Semantic Scholar.
    """
    DRAFT = "draft"
    PUBLISHED = "published"
    PENDING_ENRICHMENT = "pending_enrichment"
    ENRICHED = "enriched"
    ENRICHMENT_FAILED = "enrichment_failed"
