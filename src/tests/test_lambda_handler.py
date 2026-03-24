"""
Unit tests for the new lambda_handler entry point.
All infrastructure is mocked — no AWS or ML dependencies needed.
"""
import json
import pytest
from unittest.mock import MagicMock, patch
import lambda_handler as lh_module


class TestLambdaHandler:

    @pytest.fixture(autouse=True)
    def _setup(self):
        """Inject a mock use case before each test, reset after."""
        self.mock_uc = MagicMock()
        self.mock_uc.execute.return_value = {
            "transaction_id": "txn-123",
            "decision": "APPROVED",
            "fraud_score": 0.25,
            "method": "RandomForest-Inference",
        }
        lh_module._use_case = self.mock_uc
        yield
        lh_module._use_case = None

    def test_returns_200_on_valid_request(self):
        response = lh_module.handler({"monto": 500, "customer_id": "cust-1"}, None)
        assert response["statusCode"] == 200

    def test_response_body_contains_decision(self):
        response = lh_module.handler({"monto": 500, "customer_id": "cust-1"}, None)
        body = json.loads(response["body"])
        assert body["decision"] == "APPROVED"

    def test_response_body_contains_fraud_score(self):
        response = lh_module.handler({"monto": 500, "customer_id": "cust-1"}, None)
        body = json.loads(response["body"])
        assert body["fraud_score"] == 0.25

    def test_response_body_contains_method(self):
        response = lh_module.handler({"monto": 500, "customer_id": "cust-1"}, None)
        body = json.loads(response["body"])
        assert body["method"] == "RandomForest-Inference"

    def test_use_case_receives_correct_arguments(self):
        lh_module.handler({"monto": 750.50, "customer_id": "cust-abc"}, None)
        self.mock_uc.execute.assert_called_once_with(
            customer_id="cust-abc", amount=750.50
        )

    def test_returns_500_on_exception(self):
        self.mock_uc.execute.side_effect = Exception("model error")
        response = lh_module.handler({"monto": 100, "customer_id": "x"}, None)
        assert response["statusCode"] == 500
        body = json.loads(response["body"])
        assert "error" in body

    def test_handles_body_as_string(self):
        event = {"body": json.dumps({"monto": 200, "customer_id": "cust-2"})}
        response = lh_module.handler(event, None)
        assert response["statusCode"] == 200

    def test_returns_400_when_monto_missing(self):
        response = lh_module.handler({"customer_id": "cust-1"}, None)
        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert "monto" in body["error"]

    def test_returns_400_when_customer_id_missing(self):
        response = lh_module.handler({"monto": 500}, None)
        assert response["statusCode"] == 400
        body = json.loads(response["body"])
        assert "customer_id" in body["error"]
