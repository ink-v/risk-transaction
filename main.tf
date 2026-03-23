provider "aws" {
  region = "us-east-1"
  
  assume_role {
    role_arn = "arn:aws:iam::449112697342:role/tf-deploy-risk-transaction"
  }
}

resource "aws_dynamodb_table" "transactions_table" {
  name           = "BankingTransactions"
  billing_mode   = "PAY_PER_REQUEST"
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

locals {
  artifacts_dir = "${path.root}/lambda-artifacts"
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
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess"
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "banking_lambda" { 
  function_name    = "transaction-validator-risk"
  role             = aws_iam_role.lambda_role.arn
  handler          = "app.lambda_handler"
  runtime          = "python3.12"

  filename         = "${local.artifacts_dir}/lambda-code.zip"
  source_code_hash = filebase64sha256("${local.artifacts_dir}/lambda-code.zip")

  layers = [
    aws_lambda_layer_version.python_deps.arn
  ]
  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.transactions_table.name
    }
  }
}