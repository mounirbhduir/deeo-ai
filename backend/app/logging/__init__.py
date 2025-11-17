"""
Module logging pour DEEO.AI.

Ce module fournit le logging structuré avec structlog
pour toute l'application.
"""
from app.logging.structured_logger import (
    configure_structlog,
    get_logger,
    bind_context,
    unbind_context,
    clear_context,
    log_function_call,
    log_function_success,
    log_function_error,
)

__all__ = [
    'configure_structlog',
    'get_logger',
    'bind_context',
    'unbind_context',
    'clear_context',
    'log_function_call',
    'log_function_success',
    'log_function_error',
]
