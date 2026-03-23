resource "aws_lambda_layer_version" "python_deps" {
  layer_name          = "pandas-sklearn-layer"
  filename            = "${local.artifacts_dir}/python-deps-layer.zip"
  source_code_hash    = filebase64sha256("${local.artifacts_dir}/python-deps-layer.zip")
  compatible_runtimes = ["python3.12"]

  description = "Shared pandas, scikit-learn, joblib for banking Lambda"
}