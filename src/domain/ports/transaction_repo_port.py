"""
Port (interface) for transaction persistence.
Any database adapter must implement this contract.
"""
from abc import ABC, abstractmethod
from domain.transaction import Transaction


class TransactionRepoPort(ABC):

    @abstractmethod
    def save(self, transaction: Transaction) -> None:
        """Persist a transaction record."""
