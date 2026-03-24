"""
Tests for the domain layer: Transaction entity and abstract ports.
These tests validate business rules without any infrastructure dependency.
"""
import pytest
from domain.transaction import Transaction, TransactionStatus


class TestTransactionEntity:

    def test_create_approved_transaction(self):
        tx = Transaction(
            transaction_id="txn-001",
            customer_id="cust-123",
            amount=50.0,
            fraud_probability=0.2,
        )
        assert tx.status == TransactionStatus.APPROVED
        assert tx.risk_score == 0.2

    def test_create_declined_transaction(self):
        tx = Transaction(
            transaction_id="txn-002",
            customer_id="cust-456",
            amount=9999.0,
            fraud_probability=0.85,
        )
        assert tx.status == TransactionStatus.DECLINED

    def test_boundary_above_threshold_is_declined(self):
        tx = Transaction(
            transaction_id="txn-003",
            customer_id="cust-789",
            amount=100.0,
            fraud_probability=0.61,
        )
        assert tx.status == TransactionStatus.DECLINED

    def test_boundary_at_threshold_is_approved(self):
        tx = Transaction(
            transaction_id="txn-004",
            customer_id="cust-789",
            amount=100.0,
            fraud_probability=0.60,
        )
        assert tx.status == TransactionStatus.APPROVED

    def test_risk_score_is_rounded_to_two_decimals(self):
        tx = Transaction(
            transaction_id="txn-005",
            customer_id="cust-001",
            amount=200.0,
            fraud_probability=0.123456,
        )
        assert tx.risk_score == 0.12

    def test_transaction_has_timestamp(self):
        tx = Transaction(
            transaction_id="txn-006",
            customer_id="cust-001",
            amount=50.0,
            fraud_probability=0.1,
        )
        assert tx.timestamp is not None
        assert "Z" in tx.timestamp or "+" in tx.timestamp  # must be timezone-aware

    def test_to_dict_contains_required_keys(self):
        tx = Transaction(
            transaction_id="txn-007",
            customer_id="cust-001",
            amount=75.0,
            fraud_probability=0.3,
        )
        data = tx.to_dict()
        assert set(data.keys()) == {
            "transaction_id", "customer_id", "amount",
            "status", "risk_score", "timestamp"
        }


class TestPorts:
    """Verify that ports are abstract and cannot be instantiated directly."""

    def test_fraud_model_port_is_abstract(self):
        from domain.ports.fraud_model_port import FraudModelPort
        with pytest.raises(TypeError):
            FraudModelPort()

    def test_transaction_repo_port_is_abstract(self):
        from domain.ports.transaction_repo_port import TransactionRepoPort
        with pytest.raises(TypeError):
            TransactionRepoPort()
