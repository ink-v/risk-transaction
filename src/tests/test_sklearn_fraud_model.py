"""
Tests for SklearnFraudModel adapter.

Unit tests use mocks for joblib and sklearn to isolate the adapter logic.
Integration tests (marked) require the real model_v1.pkl and scikit-learn.
"""
import os
import pytest
from unittest.mock import patch, MagicMock
import sys
from domain.ports.fraud_model_port import FraudModelPort
from infrastructure.sklearn_fraud_model import SklearnFraudModel

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "model_v1.pkl")


class TestSklearnFraudModelUnit:
    """Unit tests: no real sklearn or pkl needed."""

    @pytest.fixture
    def model(self):
        mock_sklearn_model = MagicMock()
        mock_sklearn_model.predict_proba.return_value = [[0.3, 0.7]]
        mock_joblib = MagicMock()
        mock_joblib.load.return_value = mock_sklearn_model
        mock_pandas = MagicMock()
        mock_pandas.DataFrame.return_value = MagicMock()
        with patch.dict(sys.modules, {"joblib": mock_joblib, "pandas": mock_pandas}):
            instance = SklearnFraudModel(model_path="fake_path.pkl")
        # Keep mocks active for predict() calls
        instance._model = mock_sklearn_model
        instance._mock_pandas = mock_pandas
        return instance

    def test_implements_fraud_model_port(self, model):
        assert isinstance(model, FraudModelPort)

    def test_predict_returns_float(self, model):
        mock_pandas = MagicMock()
        mock_pandas.DataFrame.return_value = MagicMock()
        with patch.dict(sys.modules, {"pandas": mock_pandas}):
            result = model.predict(amount=500.0, hour=14)
        assert isinstance(result, float)

    def test_predict_returns_fraud_index_1(self, model):
        # predict_proba mock returns [[0.3, 0.7]] → fraud probability is index [1] = 0.7
        mock_pandas = MagicMock()
        mock_pandas.DataFrame.return_value = MagicMock()
        with patch.dict(sys.modules, {"pandas": mock_pandas}):
            result = model.predict(amount=500.0, hour=14)
        assert result == 0.7

    def test_predict_calls_model_with_correct_features(self, model):
        mock_pandas = MagicMock()
        captured_df_args = {}
        def capture_df(*args, **kwargs):
            captured_df_args["data"] = args[0] if args else None
            return MagicMock()
        mock_pandas.DataFrame.side_effect = capture_df
        with patch.dict(sys.modules, {"pandas": mock_pandas}):
            model.predict(amount=250.0, hour=10)
        # Verify DataFrame was called with correct values
        assert captured_df_args["data"] == [[250.0, 10]]

    def test_predict_zero_fraud_probability(self, model):
        model._model.predict_proba.return_value = [[1.0, 0.0]]
        mock_pandas = MagicMock()
        mock_pandas.DataFrame.return_value = MagicMock()
        with patch.dict(sys.modules, {"pandas": mock_pandas}):
            result = model.predict(amount=10.0, hour=8)
        assert result == 0.0

    def test_predict_max_fraud_probability(self, model):
        model._model.predict_proba.return_value = [[0.0, 1.0]]
        mock_pandas = MagicMock()
        mock_pandas.DataFrame.return_value = MagicMock()
        with patch.dict(sys.modules, {"pandas": mock_pandas}):
            result = model.predict(amount=99999.0, hour=2)
        assert result == 1.0


@pytest.mark.integration
class TestSklearnFraudModelIntegration:
    """Integration tests: require real model_v1.pkl and scikit-learn."""

    @pytest.fixture
    def model(self):
        if os.getenv("RUN_INTEGRATION_TESTS", "0") != "1":
            pytest.skip("Integration tests disabled. Set RUN_INTEGRATION_TESTS=1 to enable.")
        if not os.path.exists(MODEL_PATH):
            pytest.skip("model_v1.pkl not found")
        try:
            return SklearnFraudModel(model_path=MODEL_PATH)
        except Exception as e:
            pytest.skip(f"Could not load model: {e}")

    def test_predict_probability_between_0_and_1(self, model):
        result = model.predict(amount=500.0, hour=14)
        assert 0.0 <= result <= 1.0
