"""
Domain entity: Transaction.
Contains pure business logic with no infrastructure dependencies.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


FRAUD_THRESHOLD = 0.6


class TransactionStatus(str, Enum):
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"


@dataclass
class Transaction:
    transaction_id: str
    customer_id: str
    amount: float
    fraud_probability: float
    status: TransactionStatus = field(init=False)
    risk_score: float = field(init=False)
    timestamp: str = field(init=False)

    def __post_init__(self):
        self.risk_score = round(float(self.fraud_probability), 2)
        self.status = (
            TransactionStatus.DECLINED
            if self.fraud_probability > FRAUD_THRESHOLD
            else TransactionStatus.APPROVED
        )
        self.timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def to_dict(self) -> dict:
        return {
            "transaction_id": self.transaction_id,
            "customer_id": self.customer_id,
            "amount": self.amount,
            "status": self.status.value,
            "risk_score": str(self.risk_score),
            "timestamp": self.timestamp,
        }
