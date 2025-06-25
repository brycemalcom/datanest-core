# S3 Buckets for DatNest Core Platform
# Raw data lake and processed data storage

# S3 bucket for raw TSV files (32GB+ dataset)
resource "aws_s3_bucket" "raw_data" {
  bucket = "${var.s3_bucket_prefix}-raw-data-${random_string.bucket_suffix.result}"

  tags = {
    Name        = "Raw Property Data"
    Purpose     = "TSV file storage"
    Environment = var.environment
  }
}

# S3 bucket for processed/cleaned data
resource "aws_s3_bucket" "processed_data" {
  bucket = "${var.s3_bucket_prefix}-processed-data-${random_string.bucket_suffix.result}"

  tags = {
    Name        = "Processed Property Data"
    Purpose     = "ETL output storage"
    Environment = var.environment
  }
}

# S3 bucket for Lambda deployment packages
resource "aws_s3_bucket" "lambda_deployments" {
  bucket = "${var.s3_bucket_prefix}-lambda-deployments-${random_string.bucket_suffix.result}"

  tags = {
    Name        = "Lambda Deployments"
    Purpose     = "Code deployment storage"
    Environment = var.environment
  }
}

# Random string for unique bucket names
resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

# S3 bucket versioning
resource "aws_s3_bucket_versioning" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_versioning" "processed_data" {
  bucket = aws_s3_bucket.processed_data.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_versioning" "lambda_deployments" {
  bucket = aws_s3_bucket.lambda_deployments.id
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 bucket encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "processed_data" {
  bucket = aws_s3_bucket.processed_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "lambda_deployments" {
  bucket = aws_s3_bucket.lambda_deployments.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3 bucket lifecycle policies for cost optimization
resource "aws_s3_bucket_lifecycle_configuration" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id

  rule {
    id     = "raw_data_lifecycle"
    status = "Enabled"

    filter {
      prefix = ""
    }

    # Move to IA after 30 days
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    # Move to Glacier after 90 days
    transition {
      days          = 90
      storage_class = "GLACIER"
    }

    # Archive to Deep Archive after 365 days
    transition {
      days          = 365
      storage_class = "DEEP_ARCHIVE"
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "processed_data" {
  bucket = aws_s3_bucket.processed_data.id

  rule {
    id     = "processed_data_lifecycle"
    status = "Enabled"

    filter {
      prefix = ""
    }

    # Keep processed data in Standard for faster access
    # Move to IA after 60 days
    transition {
      days          = 60
      storage_class = "STANDARD_IA"
    }

    # Move to Glacier after 180 days
    transition {
      days          = 180
      storage_class = "GLACIER"
    }
  }
}

# S3 bucket notifications for Lambda triggers
resource "aws_s3_bucket_notification" "raw_data_notifications" {
  bucket = aws_s3_bucket.raw_data.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.tsv_processor.arn
    events              = ["s3:ObjectCreated:*"]
    filter_prefix       = "incoming/"
    filter_suffix       = ".tsv"
  }

  depends_on = [aws_lambda_permission.allow_s3_invoke]
}

# Public access block (security best practice)
resource "aws_s3_bucket_public_access_block" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "processed_data" {
  bucket = aws_s3_bucket.processed_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "lambda_deployments" {
  bucket = aws_s3_bucket.lambda_deployments.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
} 