"""
Tests for MLClassifierService with mocks
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.pipelines.ml_classifier import MLClassifierService, DEFAULT_AI_THEMES
from app.models import Theme


@pytest.fixture
def mock_db_session():
    """Mock database session"""
    return AsyncMock()


@pytest.fixture
def mock_classifier():
    """Mock ZeroShotClassifier"""
    classifier = Mock()
    classifier.classify = Mock(return_value=[
        {"label": "NLP", "score": 0.89},
        {"label": "ML", "score": 0.65},
        {"label": "CV", "score": 0.23}
    ])
    return classifier


@pytest.fixture
def service(mock_db_session, mock_classifier):
    """Create MLClassifierService with mocks"""
    return MLClassifierService(
        db_session=mock_db_session,
        classifier=mock_classifier
    )


class TestMLClassifierServiceInit:
    """Test service initialization"""

    def test_init_with_classifier(self, mock_db_session, mock_classifier):
        service = MLClassifierService(mock_db_session, mock_classifier)
        assert service.classifier is mock_classifier
        assert service.fallback_themes == DEFAULT_AI_THEMES

    def test_init_without_classifier(self, mock_db_session):
        with patch('app.pipelines.ml_classifier.ZeroShotClassifier.get_instance') as mock_get:
            mock_get.return_value = Mock()
            service = MLClassifierService(mock_db_session)
            assert service.classifier is not None


class TestGetCandidateLabels:
    """Test fetching candidate labels from database"""

    @pytest.mark.asyncio
    async def test_get_labels_from_db(self, service):
        # Mock theme repository
        mock_themes = [
            Mock(label="NLP"),
            Mock(label="Computer Vision"),
            Mock(label="Machine Learning")
        ]
        service.theme_repository.list = AsyncMock(return_value=mock_themes)

        labels = await service.get_candidate_labels()

        assert len(labels) == 3
        assert "NLP" in labels
        assert "Computer Vision" in labels

    @pytest.mark.asyncio
    async def test_get_labels_empty_db(self, service):
        # Mock empty database
        service.theme_repository.list = AsyncMock(return_value=[])

        labels = await service.get_candidate_labels()

        assert labels == DEFAULT_AI_THEMES

    @pytest.mark.asyncio
    async def test_get_labels_db_error(self, service):
        # Mock database error
        service.theme_repository.list = AsyncMock(
            side_effect=Exception("DB error")
        )

        labels = await service.get_candidate_labels()

        # Should fallback to default themes
        assert labels == DEFAULT_AI_THEMES


class TestClassifyPublication:
    """Test publication classification"""

    @pytest.mark.asyncio
    async def test_classify_with_title_only(self, service):
        service.theme_repository.list = AsyncMock(return_value=[
            Mock(label="NLP"),
            Mock(label="ML")
        ])

        result = await service.classify_publication(
            title="Transformers for NLP",
            top_k=2
        )

        assert len(result) == 3
        assert result[0]["label"] == "NLP"
        service.classifier.classify.assert_called_once()

    @pytest.mark.asyncio
    async def test_classify_with_title_and_abstract(self, service):
        service.theme_repository.list = AsyncMock(return_value=[
            Mock(label="NLP")
        ])

        result = await service.classify_publication(
            title="Transformers",
            abstract="Language models using attention",
            top_k=3
        )

        assert len(result) == 3
        # Check that title and abstract were combined
        call_args = service.classifier.classify.call_args
        assert "Transformers" in call_args[1]["text"]
        assert "Language models" in call_args[1]["text"]

    @pytest.mark.asyncio
    async def test_classify_empty_title(self, service):
        with pytest.raises(ValueError, match="empty"):
            await service.classify_publication(
                title="",
                top_k=3
            )

    @pytest.mark.asyncio
    async def test_classify_whitespace_title(self, service):
        with pytest.raises(ValueError, match="empty"):
            await service.classify_publication(
                title="   ",
                top_k=3
            )

    @pytest.mark.asyncio
    async def test_classify_with_empty_abstract(self, service):
        """Empty abstract should be ignored"""
        service.theme_repository.list = AsyncMock(return_value=[
            Mock(label="ML")
        ])

        result = await service.classify_publication(
            title="Neural Networks",
            abstract="",
            top_k=2
        )

        # Should use title only
        call_args = service.classifier.classify.call_args
        assert call_args[1]["text"] == "Neural Networks"

    @pytest.mark.asyncio
    async def test_classify_no_themes_available(self, service):
        service.theme_repository.list = AsyncMock(return_value=[])
        service.fallback_themes = []

        with pytest.raises(Exception, match="No themes available"):
            await service.classify_publication(
                title="Test",
                top_k=3
            )


class TestClassifyBatch:
    """Test batch classification"""

    @pytest.mark.asyncio
    async def test_classify_batch_success(self, service):
        service.theme_repository.list = AsyncMock(return_value=[
            Mock(label="NLP"),
            Mock(label="CV")
        ])

        publications = [
            {"title": "NLP with Transformers"},
            {"title": "Image Classification", "abstract": "Using CNNs"}
        ]

        results = await service.classify_batch(publications, top_k=2)

        assert len(results) == 2
        assert all(len(r) == 3 for r in results)

    @pytest.mark.asyncio
    async def test_classify_batch_empty_list(self, service):
        with pytest.raises(ValueError, match="required"):
            await service.classify_batch([], top_k=3)

    @pytest.mark.asyncio
    async def test_classify_batch_partial_failure(self, service):
        """Test batch continues even if one publication fails"""
        service.theme_repository.list = AsyncMock(return_value=[
            Mock(label="NLP")
        ])

        # Make classifier succeed for valid titles
        service.classifier.classify = Mock(side_effect=[
            [{"label": "NLP", "score": 0.9}],
            [{"label": "NLP", "score": 0.8}]
        ])

        publications = [
            {"title": "Good Title 1"},
            {"title": ""},  # Will fail validation
            {"title": "Good Title 2"}
        ]

        results = await service.classify_batch(publications, top_k=3)

        # Should have 3 results, middle one empty due to validation failure
        assert len(results) == 3
        assert len(results[0]) == 1  # Success
        assert len(results[1]) == 0  # Failed validation
        assert len(results[2]) == 1  # Success


class TestGetThemeByLabel:
    """Test theme retrieval"""

    @pytest.mark.asyncio
    async def test_get_theme_success(self, service):
        mock_theme = Mock(label="NLP")
        service.theme_repository.get_by_nom = AsyncMock(
            return_value=mock_theme
        )

        result = await service.get_theme_by_label("NLP")

        assert result is mock_theme
        service.theme_repository.get_by_nom.assert_called_once_with("NLP")

    @pytest.mark.asyncio
    async def test_get_theme_not_found(self, service):
        service.theme_repository.get_by_nom = AsyncMock(return_value=None)

        result = await service.get_theme_by_label("NonExistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_get_theme_db_error(self, service):
        service.theme_repository.get_by_nom = AsyncMock(
            side_effect=Exception("DB error")
        )

        with pytest.raises(Exception, match="DB error"):
            await service.get_theme_by_label("NLP")


class TestIntegration:
    """Integration tests with realistic scenarios"""

    @pytest.mark.asyncio
    async def test_classify_ml_paper(self, service):
        """Test classifying a Machine Learning paper"""
        service.theme_repository.list = AsyncMock(return_value=[
            Mock(label="Machine Learning"),
            Mock(label="Deep Learning"),
            Mock(label="NLP")
        ])

        service.classifier.classify = Mock(return_value=[
            {"label": "Machine Learning", "score": 0.92},
            {"label": "Deep Learning", "score": 0.78},
            {"label": "NLP", "score": 0.15}
        ])

        result = await service.classify_publication(
            title="Gradient Descent Optimization",
            abstract="Novel approaches to optimizing neural networks",
            top_k=3
        )

        assert result[0]["label"] == "Machine Learning"
        assert result[0]["score"] > 0.9

    @pytest.mark.asyncio
    async def test_classify_nlp_paper(self, service):
        """Test classifying an NLP paper"""
        service.theme_repository.list = AsyncMock(return_value=[
            Mock(label="NLP"),
            Mock(label="Machine Learning")
        ])

        service.classifier.classify = Mock(return_value=[
            {"label": "NLP", "score": 0.95},
            {"label": "Machine Learning", "score": 0.45}
        ])

        result = await service.classify_publication(
            title="Transformers for Language Understanding",
            top_k=2
        )

        assert result[0]["label"] == "NLP"
        assert result[0]["score"] > 0.9

    @pytest.mark.asyncio
    async def test_classify_cv_paper(self, service):
        """Test classifying a Computer Vision paper"""
        service.theme_repository.list = AsyncMock(return_value=[
            Mock(label="Computer Vision"),
            Mock(label="Deep Learning")
        ])

        service.classifier.classify = Mock(return_value=[
            {"label": "Computer Vision", "score": 0.88},
            {"label": "Deep Learning", "score": 0.62}
        ])

        result = await service.classify_publication(
            title="CNNs for Object Detection",
            abstract="Using convolutional networks for image analysis",
            top_k=2
        )

        assert result[0]["label"] == "Computer Vision"
        assert result[0]["score"] > 0.8


class TestFallbackBehavior:
    """Test fallback behavior when DB is unavailable"""

    @pytest.mark.asyncio
    async def test_uses_fallback_themes_on_db_failure(self, service):
        """Ensure fallback themes are used when DB fails"""
        service.theme_repository.list = AsyncMock(
            side_effect=Exception("DB connection failed")
        )

        labels = await service.get_candidate_labels()

        assert labels == DEFAULT_AI_THEMES
        assert len(labels) > 0

    @pytest.mark.asyncio
    async def test_classification_works_with_fallback(self, service):
        """Ensure classification works with fallback themes"""
        service.theme_repository.list = AsyncMock(
            side_effect=Exception("DB error")
        )

        service.classifier.classify = Mock(return_value=[
            {"label": "NLP", "score": 0.9}
        ])

        result = await service.classify_publication(
            title="Language Models",
            top_k=1
        )

        assert len(result) == 1
        assert result[0]["label"] == "NLP"
