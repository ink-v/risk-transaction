"""
Port (interface) for the fraud detection model.
Any ML adapter must implement this contract.
"""
from abc import ABC, abstractmethod


class FraudModelPort(ABC):

    @abstractmethod
    def predict(self, amount: float, hour: int) -> float:
        """Return the fraud probability (0.0 – 1.0) for a given transaction."""
