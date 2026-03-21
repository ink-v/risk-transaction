import json
import boto3
import os
import uuid
from datetime import datetime
import pandas as pd 

TABLE_NAME = os.environ.get('TABLE_NAME', 'BankingTransactions')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    try:
        body = event if isinstance(event, dict) else json.loads(event.get('body', '{}'))
        
        monto = body.get('monto', 0)
        id_cliente = body.get('id_cliente', 'ANONYMOUS')
        
        risk_score = 0.95 if monto > 5000 else 0.05
        status = "RECHAZADA" if risk_score > 0.5 else "APROBADA"

        transaction_data = {
            'transaction_id': str(uuid.uuid4()),
            'id_cliente': id_cliente,
            'monto': monto,
            'status': status,
            'risk_score': str(risk_score),
            'timestamp': datetime.utcnow().isoformat()
        }

        table.put_item(Item=transaction_data)

        return {
            'statusCode': 200,
            'body': json.dumps({
                "transaction_id": transaction_data['transaction_id'],
                "decision": status,
                "score": risk_score
            })
        }

    except Exception as e:
        print(f"Error crítico: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({"error": "Error procesando la transacción financiera"})
        }