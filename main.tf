provider "aws" {
  region = "us-east-1"
}

resource "aws_dynamodb_table" "transactions_table" {
  name           = "BankingTransactions"
  billing_mode   = "PAY_PER_REQUEST" # Ideal para Free Tier
  hash_key       = "transaction_id"

  attribute {
    name = "transaction_id"
    type = "S"
  }

  tags = {
    Environment = "Dev"
    Project     = "BankingLab"
  }
}

resource "aws_iam_role" "lambda_role" {
  name = "banking_lambda_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_dynamo_attach" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess_v2"
}