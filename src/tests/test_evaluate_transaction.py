"""
Tests for the EvaluateTransactionUseCase.
Uses mock adapters (no sklearn, no DynamoDB).
"""
import pytest
from unittest.mock import MagicMock, call
from domain.transaction import TransactionStatus
from domain.ports.fraud_model_port import FraudModelPort
from domain.ports.transaction_repo_port import TransactionRepoPort
from application.evaluate_transaction import EvaluateTransactionUseCase


class MockFraudModel(FraudModelPort):
    def __init__(self, probability: float):
        self._probability = probability

    def predict(self, amount: float, hour: int) -> float:
        return self._probability


class MockTransactionRepo(TransactionRepoPort):
    def __init__(self):
        self.saved = []

    def save(self, transaction) -> None:
        self.saved.append(transaction)


class TestEvaluateTransactionUseCase:

    def _make_use_case(self, probability: float):
        model = MockFraudModel(probability)
        repo = MockTransactionRepo()
        use_case = EvaluateTransactionUseCase(fraud_model=model, transaction_repo=repo)
        return use_case, repo

    def test_high_fraud_probability_returns_declined(self):
        use_case, _ = self._make_use_case(probability=0.9)
        result = use_case.execute(customer_id="cust-1", amount=5000.0)
        assert result["decision"] == TransactionStatus.DECLINED.value

    def test_low_fraud_probability_returns_approved(self):
        use_case, _ = self._make_use_case(probability=0.1)
        result = use_case.execute(customer_id="cust-2", amount=50.0)
        assert result["decision"] == TransactionStatus.APPROVED.value

    def test_repo_save_called_exactly_once(self):
        use_case, repo = self._make_use_case(probability=0.5)
        use_case.execute(customer_id="cust-3", amount=100.0)
        assert len(repo.saved) == 1

    def test_result_contains_required_keys(self):
        use_case, _ = self._make_use_case(probability=0.3)
        result = use_case.execute(customer_id="cust-4", amount=200.0)
        assert set(result.keys()) == {"decision", "fraud_score", "method", "transaction_id"}

    def test_fraud_score_matches_probability(self):
        use_case, _ = self._make_use_case(probability=0.75)
        result = use_case.execute(customer_id="cust-5", amount=300.0)
        assert result["fraud_score"] == 0.75

    def test_saved_transaction_customer_id_matches(self):
        use_case, repo = self._make_use_case(probability=0.2)
        use_case.execute(customer_id="cust-99", amount=150.0)
        assert repo.saved[0].customer_id == "cust-99"

    def test_saved_transaction_amount_matches(self):
        use_case, repo = self._make_use_case(probability=0.2)
        use_case.execute(customer_id="cust-10", amount=999.99)
        assert repo.saved[0].amount == 999.99

    def test_hour_is_injectable(self):
        model = MagicMock(spec=FraudModelPort)
        model.predict.return_value = 0.1
        repo = MockTransactionRepo()
        use_case = EvaluateTransactionUseCase(fraud_model=model, transaction_repo=repo)
        use_case.execute(customer_id="cust-h", amount=100.0, hour=23)
        model.predict.assert_called_once_with(amount=100.0, hour=23)
