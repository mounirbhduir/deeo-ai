"""
Tests for EmbeddingGenerator with mocks (no model download required)
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from app.ml.embedding_generator import EmbeddingGenerator


class TestEmbeddingGeneratorInit:
    """Test generator initialization"""

    def test_init_default_model(self):
        generator = EmbeddingGenerator()
        assert generator.model_name == "sentence-transformers/all-MiniLM-L6-v2"
        assert generator.model is None
        assert generator.embedding_dim is None

    def test_init_custom_model(self):
        generator = EmbeddingGenerator(model_name="custom/model")
        assert generator.model_name == "custom/model"

    def test_get_instance_singleton(self):
        instance1 = EmbeddingGenerator.get_instance()
        instance2 = EmbeddingGenerator.get_instance()
        assert instance1 is instance2


class TestModelLoading:
    """Test model loading"""

    @patch('sentence_transformers.SentenceTransformer')
    def test_load_model_success(self, mock_st):
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1] * 384])
        mock_st.return_value = mock_model

        generator = EmbeddingGenerator()
        generator._load_model()

        assert generator.model is not None
        assert generator.embedding_dim == 384

    @patch('sentence_transformers.SentenceTransformer')
    def test_load_model_cached(self, mock_st):
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1] * 384])
        mock_st.return_value = mock_model

        generator = EmbeddingGenerator()
        generator._load_model()
        generator._load_model()

        mock_st.assert_called_once()

    @patch('sentence_transformers.SentenceTransformer', side_effect=ImportError())
    def test_load_model_import_error(self, mock_st):
        generator = EmbeddingGenerator()
        with pytest.raises(ImportError, match="sentence-transformers"):
            generator._load_model()


class TestValidation:
    """Test input validation"""

    def test_encode_empty_list(self):
        generator = EmbeddingGenerator()
        with pytest.raises(ValueError, match="required"):
            generator.encode([])

    def test_encode_empty_string(self):
        generator = EmbeddingGenerator()
        with pytest.raises(ValueError, match="empty"):
            generator.encode([""])

    def test_encode_whitespace_only(self):
        generator = EmbeddingGenerator()
        with pytest.raises(ValueError, match="empty"):
            generator.encode(["   "])

    def test_encode_single_empty_text(self):
        generator = EmbeddingGenerator()
        with pytest.raises(ValueError, match="empty"):
            generator.encode_single("")


class TestEncoding:
    """Test embedding generation with mocks"""

    @patch('sentence_transformers.SentenceTransformer')
    def test_encode_single_text(self, mock_st):
        mock_model = Mock()
        mock_model.encode.side_effect = [
            np.array([[0.1] * 384]),  # For dimension check
            np.array([[0.5] * 384])   # For actual encoding
        ]
        mock_st.return_value = mock_model

        generator = EmbeddingGenerator()
        result = generator.encode("Test text")

        assert isinstance(result, np.ndarray)
        assert result.shape == (1, 384)

    @patch('sentence_transformers.SentenceTransformer')
    def test_encode_multiple_texts(self, mock_st):
        mock_model = Mock()
        mock_model.encode.side_effect = [
            np.array([[0.1] * 384]),  # For dimension check
            np.array([[0.5] * 384, [0.6] * 384, [0.7] * 384])
        ]
        mock_st.return_value = mock_model

        generator = EmbeddingGenerator()
        result = generator.encode(["Text 1", "Text 2", "Text 3"])

        assert result.shape == (3, 384)

    @patch('sentence_transformers.SentenceTransformer')
    def test_encode_single_method(self, mock_st):
        mock_model = Mock()
        mock_model.encode.side_effect = [
            np.array([[0.1] * 384]),  # For dimension check
            np.array([[0.5] * 384])
        ]
        mock_st.return_value = mock_model

        generator = EmbeddingGenerator()
        result = generator.encode_single("Test text")

        assert isinstance(result, np.ndarray)
        assert result.shape == (384,)

    @patch('sentence_transformers.SentenceTransformer')
    def test_encode_with_batch_size(self, mock_st):
        mock_model = Mock()
        mock_model.encode.side_effect = [
            np.array([[0.1] * 384]),  # For dimension check
            np.array([[0.5] * 384, [0.6] * 384])
        ]
        mock_st.return_value = mock_model

        generator = EmbeddingGenerator()
        result = generator.encode(["Text 1", "Text 2"], batch_size=1)

        assert result.shape == (2, 384)

    @patch('sentence_transformers.SentenceTransformer')
    def test_encode_with_normalization(self, mock_st):
        mock_model = Mock()
        # Normalized embeddings
        mock_model.encode.side_effect = [
            np.array([[0.1] * 384]),  # For dimension check
            np.array([[0.5] * 384]) / np.linalg.norm([0.5] * 384)
        ]
        mock_st.return_value = mock_model

        generator = EmbeddingGenerator()
        result = generator.encode("Text", normalize=True)

        # Check if normalized (approximately unit length)
        norm = np.linalg.norm(result[0])
        assert abs(norm - 1.0) < 0.01

    @patch('sentence_transformers.SentenceTransformer')
    def test_encode_string_input(self, mock_st):
        """Test that string input is converted to list"""
        mock_model = Mock()
        mock_model.encode.side_effect = [
            np.array([[0.1] * 384]),  # For dimension check
            np.array([[0.5] * 384])
        ]
        mock_st.return_value = mock_model

        generator = EmbeddingGenerator()
        result = generator.encode("Single text string")

        assert result.shape == (1, 384)


class TestEmbeddingDimension:
    """Test embedding dimension handling"""

    @patch('sentence_transformers.SentenceTransformer')
    def test_get_embedding_dimension(self, mock_st):
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1] * 384])
        mock_st.return_value = mock_model

        generator = EmbeddingGenerator()
        dim = generator.get_embedding_dimension()

        assert dim == 384

    @patch('sentence_transformers.SentenceTransformer')
    def test_embedding_dimension_cached(self, mock_st):
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1] * 384])
        mock_st.return_value = mock_model

        generator = EmbeddingGenerator()
        dim1 = generator.get_embedding_dimension()
        dim2 = generator.get_embedding_dimension()

        assert dim1 == dim2
        # Model should only be loaded once
        mock_st.assert_called_once()


class TestErrorHandling:
    """Test error handling"""

    @patch('sentence_transformers.SentenceTransformer')
    def test_encode_model_error(self, mock_st):
        mock_model = Mock()
        mock_model.encode.side_effect = [
            np.array([[0.1] * 384]),  # For dimension check
            Exception("CUDA error")
        ]
        mock_st.return_value = mock_model

        generator = EmbeddingGenerator()
        with pytest.raises(Exception, match="Embedding generation error"):
            generator.encode("Text")


class TestRealScenarios:
    """Test realistic scenarios with mocks"""

    @patch('sentence_transformers.SentenceTransformer')
    def test_research_paper_title(self, mock_st):
        mock_model = Mock()
        mock_model.encode.side_effect = [
            np.array([[0.1] * 384]),
            np.array([[0.8] * 384])
        ]
        mock_st.return_value = mock_model

        generator = EmbeddingGenerator()
        title = "Deep Learning for Computer Vision"
        result = generator.encode_single(title)

        assert result.shape == (384,)

    @patch('sentence_transformers.SentenceTransformer')
    def test_batch_papers(self, mock_st):
        mock_model = Mock()
        mock_model.encode.side_effect = [
            np.array([[0.1] * 384]),
            np.array([[0.5] * 384, [0.6] * 384, [0.7] * 384])
        ]
        mock_st.return_value = mock_model

        generator = EmbeddingGenerator()
        titles = [
            "Neural Networks for NLP",
            "Computer Vision with CNNs",
            "Reinforcement Learning Algorithms"
        ]
        result = generator.encode(titles, batch_size=3)

        assert result.shape == (3, 384)

    @patch('sentence_transformers.SentenceTransformer')
    def test_similarity_computation(self, mock_st):
        """Test that embeddings can be used for similarity"""
        mock_model = Mock()
        # Similar texts should have similar embeddings
        emb1 = np.array([0.8, 0.6, 0.0] + [0.0] * 381)
        emb2 = np.array([0.7, 0.7, 0.0] + [0.0] * 381)
        mock_model.encode.side_effect = [
            np.array([[0.1] * 384]),
            np.array([emb1, emb2])
        ]
        mock_st.return_value = mock_model

        generator = EmbeddingGenerator()
        result = generator.encode(["Text 1", "Text 2"])

        # Compute cosine similarity
        similarity = np.dot(result[0], result[1])
        assert similarity > 0.5


@pytest.mark.slow
@pytest.mark.skipif(True, reason="Requires model download")
class TestRealModel:
    """Tests with real model - manual only"""

    def test_real_encoding(self):
        generator = EmbeddingGenerator()
        result = generator.encode("Neural networks")
        assert result.shape == (1, 384)

    def test_real_batch_encoding(self):
        generator = EmbeddingGenerator()
        result = generator.encode(["Text 1", "Text 2"])
        assert result.shape == (2, 384)
