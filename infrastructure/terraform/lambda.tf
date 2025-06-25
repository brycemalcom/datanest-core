# Lambda Functions for DatNest Core Platform
# TSV processing and ETL operations

# Security group for Lambda functions
resource "aws_security_group" "lambda" {
  name        = "${var.project_name}-lambda-sg"
  description = "Security group for Lambda functions"
  vpc_id      = aws_vpc.main.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = {
    Name = "${var.project_name}-lambda-sg"
  }
}

# IAM role for Lambda functions
resource "aws_iam_role" "lambda_execution" {
  name = "${var.project_name}-lambda-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM policy for Lambda functions
resource "aws_iam_role_policy" "lambda_policy" {
  name = "${var.project_name}-lambda-policy"
  role = aws_iam_role.lambda_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.raw_data.arn,
          "${aws_s3_bucket.raw_data.arn}/*",
          aws_s3_bucket.processed_data.arn,
          "${aws_s3_bucket.processed_data.arn}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "rds-db:connect"
        ]
        Resource = aws_db_proxy.main.arn
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = aws_secretsmanager_secret.db_credentials.arn
      },
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes"
        ]
        Resource = [
          aws_sqs_queue.tsv_processing.arn,
          aws_sqs_queue.tsv_processing_dlq.arn
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "ec2:CreateNetworkInterface",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DeleteNetworkInterface"
        ]
        Resource = "*"
      }
    ]
  })
}

# Attach VPC execution policy
resource "aws_iam_role_policy_attachment" "lambda_vpc_execution" {
  role       = aws_iam_role.lambda_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

# SQS queue for TSV processing coordination
resource "aws_sqs_queue" "tsv_processing" {
  name                       = "${var.project_name}-tsv-processing"
  delay_seconds              = 0
  max_message_size           = 262144
  message_retention_seconds  = 1209600  # 14 days
  receive_wait_time_seconds  = 20       # Long polling
  visibility_timeout_seconds = 900      # 15 minutes (match Lambda timeout)

  tags = {
    Name = "${var.project_name}-tsv-processing"
  }
}

# Dead letter queue for failed processing
resource "aws_sqs_queue" "tsv_processing_dlq" {
  name = "${var.project_name}-tsv-processing-dlq"

  tags = {
    Name = "${var.project_name}-tsv-processing-dlq"
  }
}

# Main TSV processor Lambda function
resource "aws_lambda_function" "tsv_processor" {
  function_name = "${var.project_name}-tsv-processor"
  role          = aws_iam_role.lambda_execution.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = var.lambda_runtime
  timeout       = var.lambda_timeout
  memory_size   = var.lambda_memory_size

  # Placeholder for deployment package
  filename         = "tsv_processor.zip"
  source_code_hash = data.archive_file.tsv_processor_zip.output_base64sha256

  vpc_config {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.lambda.id]
  }

  environment {
    variables = {
      DB_PROXY_ENDPOINT = aws_db_proxy.main.endpoint
      DB_SECRET_ARN     = aws_secretsmanager_secret.db_credentials.arn
      S3_RAW_BUCKET     = aws_s3_bucket.raw_data.id
      S3_PROCESSED_BUCKET = aws_s3_bucket.processed_data.id
      SQS_QUEUE_URL     = aws_sqs_queue.tsv_processing.url
      ENVIRONMENT       = var.environment
    }
  }

  dead_letter_config {
    target_arn = aws_sqs_queue.tsv_processing_dlq.arn
  }

  tags = {
    Name = "${var.project_name}-tsv-processor"
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_vpc_execution,
    aws_cloudwatch_log_group.tsv_processor
  ]
}

# CloudWatch log group for TSV processor
resource "aws_cloudwatch_log_group" "tsv_processor" {
  name              = "/aws/lambda/${var.project_name}-tsv-processor"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "${var.project_name}-tsv-processor-logs"
  }
}

# Lambda permission for S3 to invoke function
resource "aws_lambda_permission" "allow_s3_invoke" {
  statement_id  = "AllowExecutionFromS3Bucket"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.tsv_processor.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.raw_data.arn
}

# Field mapping processor Lambda function
resource "aws_lambda_function" "field_mapper" {
  function_name = "${var.project_name}-field-mapper"
  role          = aws_iam_role.lambda_execution.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = var.lambda_runtime
  timeout       = var.lambda_timeout
  memory_size   = var.lambda_memory_size

  # Placeholder for deployment package
  filename         = "field_mapper.zip"
  source_code_hash = data.archive_file.field_mapper_zip.output_base64sha256

  vpc_config {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.lambda.id]
  }

  environment {
    variables = {
      DB_PROXY_ENDPOINT = aws_db_proxy.main.endpoint
      DB_SECRET_ARN     = aws_secretsmanager_secret.db_credentials.arn
      S3_PROCESSED_BUCKET = aws_s3_bucket.processed_data.id
      ENVIRONMENT       = var.environment
    }
  }

  tags = {
    Name = "${var.project_name}-field-mapper"
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_vpc_execution,
    aws_cloudwatch_log_group.field_mapper
  ]
}

# CloudWatch log group for field mapper
resource "aws_cloudwatch_log_group" "field_mapper" {
  name              = "/aws/lambda/${var.project_name}-field-mapper"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "${var.project_name}-field-mapper-logs"
  }
}

# Data quality validator Lambda function
resource "aws_lambda_function" "data_validator" {
  function_name = "${var.project_name}-data-validator"
  role          = aws_iam_role.lambda_execution.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = var.lambda_runtime
  timeout       = var.lambda_timeout
  memory_size   = var.lambda_memory_size

  # Placeholder for deployment package
  filename         = "data_validator.zip"
  source_code_hash = data.archive_file.data_validator_zip.output_base64sha256

  vpc_config {
    subnet_ids         = aws_subnet.private[*].id
    security_group_ids = [aws_security_group.lambda.id]
  }

  environment {
    variables = {
      DB_PROXY_ENDPOINT = aws_db_proxy.main.endpoint
      DB_SECRET_ARN     = aws_secretsmanager_secret.db_credentials.arn
      S3_PROCESSED_BUCKET = aws_s3_bucket.processed_data.id
      ENVIRONMENT       = var.environment
    }
  }

  tags = {
    Name = "${var.project_name}-data-validator"
  }

  depends_on = [
    aws_iam_role_policy_attachment.lambda_vpc_execution,
    aws_cloudwatch_log_group.data_validator
  ]
}

# CloudWatch log group for data validator
resource "aws_cloudwatch_log_group" "data_validator" {
  name              = "/aws/lambda/${var.project_name}-data-validator"
  retention_in_days = var.log_retention_days

  tags = {
    Name = "${var.project_name}-data-validator-logs"
  }
}

# Placeholder deployment packages (will be replaced with actual code)
data "archive_file" "tsv_processor_zip" {
  type        = "zip"
  output_path = "tsv_processor.zip"
  source {
    content  = "def lambda_handler(event, context): return {'statusCode': 200}"
    filename = "lambda_function.py"
  }
}

data "archive_file" "field_mapper_zip" {
  type        = "zip"
  output_path = "field_mapper.zip"
  source {
    content  = "def lambda_handler(event, context): return {'statusCode': 200}"
    filename = "lambda_function.py"
  }
}

data "archive_file" "data_validator_zip" {
  type        = "zip"
  output_path = "data_validator.zip"
  source {
    content  = "def lambda_handler(event, context): return {'statusCode': 200}"
    filename = "lambda_function.py"
  }
} 