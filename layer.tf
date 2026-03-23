# Construir dependencias de Python para la Layer
resource "null_resource" "build_python_layer" {
  triggers = {
    requirements_hash = filemd5("${path.module}/layers/requirements.txt")
  }

  provisioner "local-exec" {
    interpreter = ["cmd", "/C"]
    command     = <<-EOT
      echo Building Python deps layer...
      if exist layers\\python-deps rmdir /S /Q layers\\python-deps
      mkdir layers\\python-deps
      pip install --upgrade pip
      pip install -r layers\\requirements.txt -t layers\\python-deps
    EOT
  }
}

data "archive_file" "python_layer_zip" {
  depends_on  = [null_resource.build_python_layer]
  type        = "zip"
  source_dir  = "${path.module}/layers/python-deps"
  output_path = "${path.module}/dist/python-deps-layer.zip"
}

resource "aws_lambda_layer_version" "python_deps" {
  layer_name          = "pandas-sklearn-layer"
  filename            = data.archive_file.python_layer_zip.output_path
  source_code_hash    = data.archive_file.python_layer_zip.output_base64sha256
  compatible_runtimes = ["python3.12"]

  description = "Shared pandas, scikit-learn, joblib for banking Lambda"
}