resource "null_resource" "build_python_layer" {
  triggers = {
    requirements_hash = filemd5("${path.root}/layers/requirements.txt")
  }


  provisioner "local-exec" {
    interpreter = ["cmd", "/C"]
    command     = <<-EOT
      echo Building Python deps layer...
      if exist layers\\python-deps rmdir /S /Q layers\\python-deps
      mkdir layers\\python-deps
      pip --version || (echo pip not found & exit /b 1)
      pip install --upgrade pip || exit /b 1
      pip install -r layers\\requirements.txt -t layers\\python-deps || exit /b 1
    EOT
  }
}

data "archive_file" "python_layer_zip" {
  depends_on  = [null_resource.build_python_layer]
  type        = "zip"
  source_dir  = "${path.root}/layers/python-deps"
  output_path = "${path.root}/dist/python-deps-layer.zip"
}

resource "aws_lambda_layer_version" "python_deps" {
  layer_name          = "pandas-sklearn-layer"
  filename            = data.archive_file.python_layer_zip.output_path
  source_code_hash    = data.archive_file.python_layer_zip.output_base64sha256
  compatible_runtimes = ["python3.12"]

  description = "Shared pandas, scikit-learn, joblib for banking Lambda"
}