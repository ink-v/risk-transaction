"""
Use case: EvaluateTransactionUseCase.
Orchestrates fraud detection and transaction persistence.
"""
import uuid
from datetime import datetime

from domain.transaction import Transaction
from domain.ports.fraud_model_port import FraudModelPort
from domain.ports.transaction_repo_port import TransactionRepoPort


class EvaluateTransactionUseCase:

    def __init__(self, fraud_model: FraudModelPort, transaction_repo: TransactionRepoPort):
        self._model = fraud_model
        self._repo = transaction_repo

    def execute(self, customer_id: str, amount: float, hour: int | None = None) -> dict:
        if hour is None:
            hour = datetime.now().hour
        fraud_probability = self._model.predict(amount=amount, hour=hour)

        transaction = Transaction(
            transaction_id=str(uuid.uuid4()),
            customer_id=customer_id,
            amount=amount,
            fraud_probability=fraud_probability,
        )

        self._repo.save(transaction)

        return {
            "transaction_id": transaction.transaction_id,
            "decision": transaction.status.value,
            "fraud_score": transaction.risk_score,
            "method": "RandomForest-Inference",
        }
