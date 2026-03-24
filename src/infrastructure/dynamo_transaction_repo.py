"""
Adapter: DynamoDB implementation of TransactionRepoPort.
Persists Transaction entities to an AWS DynamoDB table.
"""
from domain.ports.transaction_repo_port import TransactionRepoPort
from domain.transaction import Transaction


class DynamoTransactionRepo(TransactionRepoPort):

    def __init__(self, table):
        self._table = table

    def save(self, transaction: Transaction) -> None:
        self._table.put_item(Item=transaction.to_dict())
