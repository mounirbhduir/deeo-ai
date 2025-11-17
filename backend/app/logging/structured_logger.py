"""
Configuration du logging structuré avec structlog.

Ce module configure structlog pour produire des logs JSON structurés
avec contexte enrichi, traçabilité et niveaux configurables.
"""
import logging
import sys
from typing import Any, Dict, Optional

import structlog
from structlog.types import EventDict, Processor


def add_app_context(
    logger: logging.Logger, method_name: str, event_dict: EventDict
) -> EventDict:
    """
    Ajoute contexte application à tous les logs.
    
    Args:
        logger: Logger instance
        method_name: Nom de la méthode de logging
        event_dict: Dictionnaire événement
        
    Returns:
        Event dict enrichi
    """
    event_dict["app"] = "deeo-ai"
    event_dict["environment"] = "development"  # TODO: from config
    return event_dict


def drop_color_message_key(
    logger: logging.Logger, method_name: str, event_dict: EventDict
) -> EventDict:
    """
    Supprime la clé 'color_message' pour éviter duplication en JSON.
    
    Args:
        logger: Logger instance
        method_name: Nom méthode
        event_dict: Dict événement
        
    Returns:
        Event dict nettoyé
    """
    event_dict.pop("color_message", None)
    return event_dict


def configure_structlog(
    log_level: str = "INFO",
    json_logs: bool = True,
    log_file: Optional[str] = None
) -> None:
    """
    Configure structlog pour l'application.
    
    Args:
        log_level: Niveau de log (DEBUG, INFO, WARNING, ERROR)
        json_logs: Si True, logs en JSON. Si False, logs colorés console
        log_file: Chemin fichier log optionnel
    """
    # Conversion log level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Processeurs structlog communs
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        add_app_context,
    ]
    
    # Configuration selon format souhaité
    if json_logs:
        # Logs JSON pour production
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            drop_color_message_key,
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Logs colorés pour développement
        processors = shared_processors + [
            structlog.processors.ExceptionPrettyPrinter(),
            structlog.dev.ConsoleRenderer(colors=True),
        ]
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure logging stdlib
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=numeric_level,
    )
    
    # Ajouter handler fichier si spécifié
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        
        if json_logs:
            # Format JSON pour fichier
            file_handler.setFormatter(
                logging.Formatter("%(message)s")
            )
        else:
            # Format standard
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )
        
        logging.getLogger().addHandler(file_handler)
    
    # Réduire verbosité de certaines librairies
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Récupère un logger structlog.
    
    Args:
        name: Nom du logger (généralement __name__)
        
    Returns:
        Logger structlog configuré
        
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("user.created", user_id=123, email="test@example.com")
    """
    return structlog.get_logger(name)


# ===== Contexte Global (Thread-safe) =====

def bind_context(**kwargs: Any) -> None:
    """
    Ajoute contexte global à tous les logs suivants dans le thread actuel.
    
    Args:
        **kwargs: Paires clé-valeur à ajouter au contexte
        
    Example:
        >>> bind_context(request_id="abc-123", user_id=456)
        >>> logger.info("action.performed")  # Inclura request_id et user_id
    """
    structlog.contextvars.bind_contextvars(**kwargs)


def unbind_context(*keys: str) -> None:
    """
    Retire des clés du contexte global.
    
    Args:
        *keys: Clés à retirer
        
    Example:
        >>> unbind_context("request_id", "user_id")
    """
    structlog.contextvars.unbind_contextvars(*keys)


def clear_context() -> None:
    """
    Vide complètement le contexte global.
    
    Utile au début/fin de requêtes pour éviter fuites de contexte.
    """
    structlog.contextvars.clear_contextvars()


# ===== Helpers pour Patterns Communs =====

def log_function_call(
    logger: structlog.stdlib.BoundLogger,
    function_name: str,
    **kwargs: Any
) -> None:
    """
    Log standardisé pour appel de fonction.
    
    Args:
        logger: Logger structlog
        function_name: Nom de la fonction
        **kwargs: Arguments de la fonction
        
    Example:
        >>> log_function_call(logger, "process_publication", publication_id=123)
    """
    logger.debug(
        f"{function_name}.called",
        function=function_name,
        **kwargs
    )


def log_function_success(
    logger: structlog.stdlib.BoundLogger,
    function_name: str,
    duration_ms: Optional[float] = None,
    **kwargs: Any
) -> None:
    """
    Log standardisé pour succès fonction.
    
    Args:
        logger: Logger structlog
        function_name: Nom fonction
        duration_ms: Durée en millisecondes
        **kwargs: Données supplémentaires
    """
    log_data = {"function": function_name, **kwargs}
    if duration_ms is not None:
        log_data["duration_ms"] = duration_ms
    
    logger.info(f"{function_name}.success", **log_data)


def log_function_error(
    logger: structlog.stdlib.BoundLogger,
    function_name: str,
    error: Exception,
    **kwargs: Any
) -> None:
    """
    Log standardisé pour erreur fonction.
    
    Args:
        logger: Logger structlog
        function_name: Nom fonction
        error: Exception levée
        **kwargs: Contexte supplémentaire
    """
    logger.error(
        f"{function_name}.error",
        function=function_name,
        error_type=type(error).__name__,
        error_message=str(error),
        **kwargs,
        exc_info=True
    )
