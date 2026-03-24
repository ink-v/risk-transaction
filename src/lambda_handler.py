"""
AWS Lambda entry point.
Wires infrastructure adapters to the use case following hexagonal architecture.
"""
import json
import os


_use_case = None


def _get_use_case():
    """Lazy initialization — only runs on first invocation (Lambda warm-start friendly)."""
    global _use_case
    if _use_case is None:
        import boto3
        from application.evaluate_transaction import EvaluateTransactionUseCase
        from infrastructure.sklearn_fraud_model import SklearnFraudModel
        from infrastructure.dynamo_transaction_repo import DynamoTransactionRepo

        model_path = os.environ.get(
            "MODEL_PATH", os.path.join(os.path.dirname(__file__), "model_v1.pkl")
        )
        table_name = os.environ.get("TABLE_NAME", "BankingTransactions")

        fraud_model = SklearnFraudModel(model_path=model_path)
        dynamodb = boto3.resource("dynamodb")
        table = dynamodb.Table(table_name)
        transaction_repo = DynamoTransactionRepo(table=table)

        _use_case = EvaluateTransactionUseCase(
            fraud_model=fraud_model, transaction_repo=transaction_repo
        )
    return _use_case


def handler(event, context):
    try:
        if isinstance(event, dict) and "body" in event:
            body = json.loads(event["body"])
        else:
            body = event if isinstance(event, dict) else json.loads(event)

        if "monto" not in body:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing required field: monto"}),
            }
        if "customer_id" not in body:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing required field: customer_id"}),
            }

        amount = float(body["monto"])
        customer_id = body["customer_id"]

        result = _get_use_case().execute(customer_id=customer_id, amount=amount)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "decision": result["decision"],
                "fraud_score": result["fraud_score"],
                "method": result["method"],
            }),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }
