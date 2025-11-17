"""
Tests for ZeroShotClassifier with mocks (no model download required)
"""

import pytest
from unittest.mock import Mock, patch
from app.ml.zero_shot_classifier import ZeroShotClassifier


class TestZeroShotClassifierInit:
    """Test classifier initialization"""

    def test_init_default_model(self):
        classifier = ZeroShotClassifier()
        assert classifier.model_name == "facebook/bart-large-mnli"
        assert classifier.pipeline is None

    def test_init_custom_model(self):
        classifier = ZeroShotClassifier(model_name="custom/model")
        assert classifier.model_name == "custom/model"

    def test_get_instance_singleton(self):
        instance1 = ZeroShotClassifier.get_instance()
        instance2 = ZeroShotClassifier.get_instance()
        assert instance1 is instance2


class TestModelLoading:
    """Test model loading"""

    @patch('transformers.pipeline')
    def test_load_model_success(self, mock_pipeline):
        mock_pipeline.return_value = Mock()
        classifier = ZeroShotClassifier()
        classifier._load_model()
        assert classifier.pipeline is not None

    @patch('transformers.pipeline')
    def test_load_model_cached(self, mock_pipeline):
        mock_pipeline.return_value = Mock()
        classifier = ZeroShotClassifier()
        classifier._load_model()
        classifier._load_model()
        mock_pipeline.assert_called_once()

    @patch('transformers.pipeline', side_effect=ImportError())
    def test_load_model_import_error(self, mock_pipeline):
        classifier = ZeroShotClassifier()
        with pytest.raises(ImportError, match="transformers"):
            classifier._load_model()


class TestValidation:
    """Test input validation"""

    def test_empty_text(self):
        classifier = ZeroShotClassifier()
        with pytest.raises(ValueError, match="empty"):
            classifier.classify("", ["label"])

    def test_whitespace_text(self):
        classifier = ZeroShotClassifier()
        with pytest.raises(ValueError, match="empty"):
            classifier.classify("   ", ["label"])

    def test_no_labels(self):
        classifier = ZeroShotClassifier()
        with pytest.raises(ValueError, match="required"):
            classifier.classify("text", [])


class TestClassification:
    """Test classification with mocks"""

    @patch('transformers.pipeline')
    def test_single_label(self, mock_pipeline):
        mock_pipe = Mock()
        mock_pipe.return_value = {
            "labels": ["CV"],
            "scores": [0.95]
        }
        mock_pipeline.return_value = mock_pipe

        classifier = ZeroShotClassifier()
        results = classifier.classify("text", ["CV"], top_k=1)

        assert len(results) == 1
        assert results[0]["label"] == "CV"
        assert results[0]["score"] == 0.95

    @patch('transformers.pipeline')
    def test_multi_label(self, mock_pipeline):
        mock_pipe = Mock()
        mock_pipe.return_value = {
            "labels": ["CV", "ML", "NLP"],
            "scores": [0.85, 0.65, 0.25]
        }
        mock_pipeline.return_value = mock_pipe

        classifier = ZeroShotClassifier()
        results = classifier.classify("text", ["CV", "NLP", "ML"], top_k=3)

        assert len(results) == 3
        assert results[0]["label"] == "CV"

    @patch('transformers.pipeline')
    def test_top_k_limit(self, mock_pipeline):
        mock_pipe = Mock()
        mock_pipe.return_value = {
            "labels": ["L1", "L2", "L3", "L4"],
            "scores": [0.9, 0.7, 0.5, 0.3]
        }
        mock_pipeline.return_value = mock_pipe

        classifier = ZeroShotClassifier()
        results = classifier.classify("text", ["L1", "L2", "L3", "L4"], top_k=2)

        assert len(results) == 2

    @patch('transformers.pipeline')
    def test_score_range(self, mock_pipeline):
        mock_pipe = Mock()
        mock_pipe.return_value = {
            "labels": ["L1", "L2"],
            "scores": [0.85, 0.15]
        }
        mock_pipeline.return_value = mock_pipe

        classifier = ZeroShotClassifier()
        results = classifier.classify("text", ["L1", "L2"])

        for r in results:
            assert 0.0 <= r["score"] <= 1.0

    @patch('transformers.pipeline')
    def test_result_format(self, mock_pipeline):
        mock_pipe = Mock()
        mock_pipe.return_value = {
            "labels": ["L1"],
            "scores": [0.9]
        }
        mock_pipeline.return_value = mock_pipe

        classifier = ZeroShotClassifier()
        results = classifier.classify("text", ["L1"])

        assert isinstance(results, list)
        assert "label" in results[0]
        assert "score" in results[0]


class TestErrorHandling:
    """Test error handling"""

    @patch('transformers.pipeline')
    def test_pipeline_error(self, mock_pipeline):
        mock_pipe = Mock()
        mock_pipe.side_effect = Exception("CUDA error")
        mock_pipeline.return_value = mock_pipe

        classifier = ZeroShotClassifier()
        with pytest.raises(Exception, match="Classification error"):
            classifier.classify("text", ["L1"])


class TestRealScenarios:
    """Test realistic scenarios with mocks"""

    @patch('transformers.pipeline')
    def test_ml_paper(self, mock_pipeline):
        mock_pipe = Mock()
        mock_pipe.return_value = {
            "labels": ["Machine Learning", "CV", "NLP"],
            "scores": [0.92, 0.15, 0.08]
        }
        mock_pipeline.return_value = mock_pipe

        classifier = ZeroShotClassifier()
        text = "Neural network optimization"
        results = classifier.classify(text, ["Machine Learning", "NLP", "CV"], top_k=3)

        assert results[0]["label"] == "Machine Learning"
        assert results[0]["score"] > 0.9

    @patch('transformers.pipeline')
    def test_nlp_paper(self, mock_pipeline):
        mock_pipe = Mock()
        mock_pipe.return_value = {
            "labels": ["NLP", "ML", "CV"],
            "scores": [0.95, 0.45, 0.05]
        }
        mock_pipeline.return_value = mock_pipe

        classifier = ZeroShotClassifier()
        text = "Transformer language models"
        results = classifier.classify(text, ["NLP", "ML", "CV"], top_k=2)

        assert results[0]["label"] == "NLP"

    @patch('transformers.pipeline')
    def test_cv_paper(self, mock_pipeline):
        mock_pipe = Mock()
        mock_pipe.return_value = {
            "labels": ["CV", "ML", "Robotics"],
            "scores": [0.88, 0.62, 0.15]
        }
        mock_pipeline.return_value = mock_pipe

        classifier = ZeroShotClassifier()
        text = "CNN for object detection"
        results = classifier.classify(text, ["CV", "ML", "Robotics"], top_k=3)

        assert results[0]["label"] == "CV"


@pytest.mark.slow
@pytest.mark.skipif(True, reason="Requires model download")
class TestRealModel:
    """Tests with real model - manual only"""

    def test_real_classification(self):
        classifier = ZeroShotClassifier()
        results = classifier.classify(
            "Neural networks for vision",
            ["CV", "NLP", "Robotics"],
            top_k=2
        )
        assert len(results) == 2
