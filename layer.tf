resource "aws_lambda_layer_version" "python_deps" {
  layer_name          = "data-core-layer"
  filename            = "${local.artifacts_dir}/data-core-layer.zip"
  source_code_hash    = filebase64sha256("${local.artifacts_dir}/data-core-layer.zip")
  compatible_runtimes = ["python3.12"]

  description = "Shared pandas banking Lambda"
}

resource "aws_lambda_layer_version" "ml_core" {
  layer_name          = "ml-core-layer"
  filename            = "${local.artifacts_dir}/ml-core-layer.zip"
  source_code_hash    = filebase64sha256("${local.artifacts_dir}/ml-core-layer.zip")
  compatible_runtimes = ["python3.12"]

  description = "scikit-learn + joblib for banking Lambda"
}