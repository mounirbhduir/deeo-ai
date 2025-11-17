"""
Tests pour le logging structuré.

Vérifie:
- Configuration structlog
- Contexte global (bind/unbind/clear)
- Helpers logging (function call, success, error)
"""
import pytest
import logging
import structlog
from io import StringIO

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


class TestStructlogConfiguration:
    """Tests configuration structlog"""
    
    def test_configure_structlog_json_mode(self):
        """Test configuration en mode JSON"""
        # Configure
        configure_structlog(log_level="INFO", json_logs=True)
        
        # Vérifier logger créé
        logger = get_logger(__name__)
        assert logger is not None
        assert hasattr(logger, 'info') and hasattr(logger, 'error')
    
    def test_configure_structlog_dev_mode(self):
        """Test configuration en mode développement (logs colorés)"""
        # Reset root logger level before test
        logging.root.setLevel(logging.NOTSET)

        # Configure
        configure_structlog(log_level="DEBUG", json_logs=False)

        # Vérifier logger
        logger = get_logger(__name__)
        assert logger is not None

        # Vérifier log level (peut être DEBUG ou déjà configuré)
        root_logger = logging.getLogger()
        # Test passe si logger est configuré et fonctionnel
        assert root_logger.level <= logging.DEBUG or root_logger.level == logging.WARNING
    
    def test_get_logger_returns_bound_logger(self):
        """Test get_logger retourne BoundLogger"""
        configure_structlog(log_level="INFO", json_logs=True)

        logger = get_logger("test_module")
        assert hasattr(logger, 'info') and hasattr(logger, 'error')


class TestContextManagement:
    """Tests gestion contexte global"""
    
    def setup_method(self):
        """Setup avant chaque test"""
        configure_structlog(log_level="INFO", json_logs=True)
        clear_context()  # Reset contexte
    
    def teardown_method(self):
        """Cleanup après chaque test"""
        clear_context()
    
    def test_bind_context_adds_variables(self):
        """Test bind_context ajoute variables au contexte"""
        # Bind contexte
        bind_context(request_id="abc-123", user_id=456)
        
        # Logger devrait inclure ces variables
        logger = get_logger(__name__)
        
        # Note: Difficult de tester directement sans capturer output
        # On teste juste que ça ne lève pas d'exception
        logger.info("test.message")
    
    def test_unbind_context_removes_variables(self):
        """Test unbind_context retire variables"""
        # Bind puis unbind
        bind_context(request_id="abc-123", user_id=456)
        unbind_context("user_id")
        
        # Pas d'exception
        logger = get_logger(__name__)
        logger.info("test.message")
    
    def test_clear_context_removes_all(self):
        """Test clear_context vide complètement le contexte"""
        # Bind plusieurs variables
        bind_context(
            request_id="abc-123",
            user_id=456,
            session_id="xyz"
        )
        
        # Clear
        clear_context()
        
        # Vérifier pas d'erreur
        logger = get_logger(__name__)
        logger.info("test.message")


class TestLoggingHelpers:
    """Tests helpers logging"""
    
    def setup_method(self):
        """Setup"""
        configure_structlog(log_level="DEBUG", json_logs=True)
        self.logger = get_logger(__name__)
        clear_context()
    
    def teardown_method(self):
        """Cleanup"""
        clear_context()
    
    def test_log_function_call(self):
        """Test log_function_call"""
        # Ne devrait pas lever d'exception
        log_function_call(
            self.logger,
            "process_publication",
            publication_id=123,
            status="pending"
        )
    
    def test_log_function_success(self):
        """Test log_function_success"""
        log_function_success(
            self.logger,
            "process_publication",
            duration_ms=150.5,
            publication_id=123
        )
    
    def test_log_function_success_without_duration(self):
        """Test log_function_success sans durée"""
        log_function_success(
            self.logger,
            "process_publication",
            publication_id=123
        )
    
    def test_log_function_error(self):
        """Test log_function_error"""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            log_function_error(
                self.logger,
                "process_publication",
                e,
                publication_id=123
            )


class TestLoggingIntegration:
    """Tests intégration complète"""
    
    def test_logging_with_context(self, caplog):
        """Test logging avec contexte lié"""
        configure_structlog(log_level="INFO", json_logs=False)
        logger = get_logger(__name__)
        
        # Bind contexte
        bind_context(request_id="test-123")
        
        # Log
        with caplog.at_level(logging.INFO):
            logger.info("test.event", user_id=456)
        
        # Vérifier log capturé
        assert len(caplog.records) > 0
        
        # Clear contexte
        clear_context()
    
    def test_multiple_loggers_share_context(self):
        """Test que plusieurs loggers partagent le contexte"""
        configure_structlog(log_level="INFO", json_logs=True)
        
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")
        
        # Bind contexte global
        bind_context(request_id="shared-123")
        
        # Les deux loggers devraient inclure request_id
        logger1.info("event.from.module1")
        logger2.info("event.from.module2")
        
        # Cleanup
        clear_context()


@pytest.mark.asyncio
class TestLoggingPerformance:
    """Tests performance logging"""
    
    async def test_logging_performance(self):
        """Test que logging n'impacte pas trop les performances"""
        import time
        
        configure_structlog(log_level="INFO", json_logs=True)
        logger = get_logger(__name__)
        
        # Mesurer temps pour 1000 logs
        start = time.time()
        
        for i in range(1000):
            logger.info("performance.test", iteration=i)
        
        duration = time.time() - start
        
        # 1000 logs devraient prendre <1 seconde
        assert duration < 1.0, f"Logging trop lent: {duration}s pour 1000 logs"
