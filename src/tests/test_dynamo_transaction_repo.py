"""
Unit tests for DynamoTransactionRepo adapter.
All boto3 calls are mocked — no real AWS connection needed.
"""
import pytest
from unittest.mock import MagicMock, patch
from domain.transaction import Transaction
from infrastructure.dynamo_transaction_repo import DynamoTransactionRepo


class TestDynamoTransactionRepo:

    def _make_transaction(self, fraud_prob=0.3):
        return Transaction(
            transaction_id="txn-001",
            customer_id="cust-abc",
            amount=250.0,
            fraud_probability=fraud_prob,
        )

    def test_implements_transaction_repo_port(self):
        from domain.ports.transaction_repo_port import TransactionRepoPort
        mock_table = MagicMock()
        repo = DynamoTransactionRepo(table=mock_table)
        assert isinstance(repo, TransactionRepoPort)

    def test_save_calls_put_item(self):
        mock_table = MagicMock()
        repo = DynamoTransactionRepo(table=mock_table)
        txn = self._make_transaction()

        repo.save(txn)

        mock_table.put_item.assert_called_once()

    def test_save_passes_correct_item(self):
        mock_table = MagicMock()
        repo = DynamoTransactionRepo(table=mock_table)
        txn = self._make_transaction(fraud_prob=0.45)

        repo.save(txn)

        item = mock_table.put_item.call_args[1]["Item"]
        assert item["transaction_id"] == "txn-001"
        assert item["customer_id"] == "cust-abc"
        assert item["amount"] == 250.0
        assert item["status"] == "APPROVED"
        assert item["risk_score"] == "0.45"
        assert "timestamp" in item

    def test_save_declined_transaction(self):
        mock_table = MagicMock()
        repo = DynamoTransactionRepo(table=mock_table)
        txn = self._make_transaction(fraud_prob=0.85)

        repo.save(txn)

        item = mock_table.put_item.call_args[1]["Item"]
        assert item["status"] == "DECLINED"
        assert item["risk_score"] == "0.85"

    def test_save_propagates_dynamodb_error(self):
        mock_table = MagicMock()
        mock_table.put_item.side_effect = Exception("DynamoDB unreachable")
        repo = DynamoTransactionRepo(table=mock_table)
        txn = self._make_transaction()

        with pytest.raises(Exception, match="DynamoDB unreachable"):
            repo.save(txn)
