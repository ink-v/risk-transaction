import json
import boto3
import os
import uuid
import joblib

from datetime import datetime, timezone

# Load the model when Lambda starts (warm start).
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model_v1.pkl')
model = joblib.load(MODEL_PATH)

TABLE_NAME = os.environ.get('TABLE_NAME', 'BankingTransactions')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):
    try:
        body = event if isinstance(event, dict) else json.loads(event.get('body', '{}'))
        
        monto = float(body.get('monto', 0))
        hora = int(datetime.now().hour)  # Use the current hour as a model feature.
        
        # Build input data using the same schema as training.
        input_data = pd.DataFrame([[monto, hora]], columns=['monto', 'hora'])
        
        # Run the model and take the fraud probability
        # Returns prediction of the probability
        fraud_probability = model.predict_proba(input_data)[0][1]
        
        status = "DECLINED" if fraud_probability > 0.6 else "APPROVED"
        risk_score = round(float(fraud_probability), 2)        
        customer_id = body.get('customer_id', '')
        timestamp = datetime.now(timezone.utc).isoformat()

        transaction_data = {
            'transaction_id': str(uuid.uuid4()),
            'customer_id': customer_id,
            'amount': monto,
            'status': status,
            'risk_score': str(risk_score),
            'timestamp': timestamp
        }

        table.put_item(Item=transaction_data)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "decision": status,
                "fraud_score": risk_score,
                "method": "RandomForest-Inference"
            })
        }
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}