# DatNest Core Platform - Terraform Outputs
# Key infrastructure information for application configuration

# VPC Information
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

# Subnet Information
output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = aws_subnet.private[*].id
}

# S3 Bucket Information
output "s3_raw_data_bucket" {
  description = "Name of the S3 bucket for raw TSV data"
  value       = aws_s3_bucket.raw_data.id
}

output "s3_processed_data_bucket" {
  description = "Name of the S3 bucket for processed data"
  value       = aws_s3_bucket.processed_data.id
}

output "s3_lambda_deployments_bucket" {
  description = "Name of the S3 bucket for Lambda deployments"
  value       = aws_s3_bucket.lambda_deployments.id
}

# Database Information
output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}

output "rds_port" {
  description = "RDS instance port"
  value       = aws_db_instance.main.port
}

output "db_proxy_endpoint" {
  description = "RDS Proxy endpoint for Lambda connections"
  value       = aws_db_proxy.main.endpoint
  sensitive   = true
}

output "database_name" {
  description = "Name of the PostgreSQL database"
  value       = aws_db_instance.main.db_name
}

# Secrets Manager
output "db_credentials_secret_arn" {
  description = "ARN of the database credentials secret in Secrets Manager"
  value       = aws_secretsmanager_secret.db_credentials.arn
  sensitive   = true
}

# Lambda Functions
output "lambda_tsv_processor_function_name" {
  description = "Name of the TSV processor Lambda function"
  value       = aws_lambda_function.tsv_processor.function_name
}

output "lambda_field_mapper_function_name" {
  description = "Name of the field mapper Lambda function"
  value       = aws_lambda_function.field_mapper.function_name
}

output "lambda_data_validator_function_name" {
  description = "Name of the data validator Lambda function"
  value       = aws_lambda_function.data_validator.function_name
}

# SQS Queues
output "sqs_tsv_processing_queue_url" {
  description = "URL of the SQS queue for TSV processing"
  value       = aws_sqs_queue.tsv_processing.url
}

output "sqs_tsv_processing_queue_arn" {
  description = "ARN of the SQS queue for TSV processing"
  value       = aws_sqs_queue.tsv_processing.arn
}

# IAM Roles
output "lambda_execution_role_arn" {
  description = "ARN of the Lambda execution role"
  value       = aws_iam_role.lambda_execution.arn
}

# Security Groups
output "rds_security_group_id" {
  description = "ID of the RDS security group"
  value       = aws_security_group.rds.id
}

output "lambda_security_group_id" {
  description = "ID of the Lambda security group"
  value       = aws_security_group.lambda.id
}

# Environment Configuration for Applications
output "environment_config" {
  description = "Environment configuration for applications"
  value = {
    environment           = var.environment
    aws_region           = var.aws_region
    project_name         = var.project_name
    db_proxy_endpoint    = aws_db_proxy.main.endpoint
    db_secret_arn        = aws_secretsmanager_secret.db_credentials.arn
    s3_raw_bucket        = aws_s3_bucket.raw_data.id
    s3_processed_bucket  = aws_s3_bucket.processed_data.id
    sqs_queue_url        = aws_sqs_queue.tsv_processing.url
  }
  sensitive = true
}

# Cost Optimization Info
output "cost_optimization_info" {
  description = "Information about cost optimization features enabled"
  value = {
    s3_lifecycle_policies_enabled = true
    rds_multi_az_enabled         = true
    rds_backup_retention_days    = var.backup_retention_period
    cloudwatch_log_retention_days = var.log_retention_days
  }
}

# Connection Information for Development
output "development_connection_info" {
  description = "Connection information for development and testing"
  value = {
    vpc_id                = aws_vpc.main.id
    private_subnet_ids    = aws_subnet.private[*].id
    rds_security_group_id = aws_security_group.rds.id
    db_proxy_endpoint     = aws_db_proxy.main.endpoint
    database_port         = aws_db_instance.main.port
  }
  sensitive = true
}

# Bastion Host Outputs
output "bastion_public_ip" {
  value       = aws_eip.bastion.public_ip
  description = "Public IP address of the bastion host"
}

output "bastion_instance_id" {
  value       = aws_instance.bastion.id
  description = "Instance ID of the bastion host"
}

output "bastion_ssh_command" {
  value       = "ssh -i ~/.ssh/datnest_bastion ec2-user@${aws_eip.bastion.public_ip}"
  description = "SSH command to connect to bastion host"
}

output "database_tunnel_command" {
  value       = "ssh -i ~/.ssh/datnest_bastion -L 5432:${aws_db_instance.main.endpoint}:5432 ec2-user@${aws_eip.bastion.public_ip}"
  description = "SSH tunnel command for database access"
} 