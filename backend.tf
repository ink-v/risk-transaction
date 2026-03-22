terraform {
  backend "s3" {
    bucket         = "banking-transaction-tf-state"
    key            = "risk-transactions/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-locks"
  }
}