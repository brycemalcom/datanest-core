# DatNest Core Platform - Terraform Variables
# Configuration for AWS infrastructure deployment

variable "aws_region" {
  description = "AWS region for infrastructure deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "datnest-core"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

# RDS Configuration
variable "db_instance_class" {
  description = "RDS instance class for PostgreSQL"
  type        = string
  default     = "db.r5.xlarge"  # Optimized for 150M+ records
}

variable "db_allocated_storage" {
  description = "Initial storage allocation for RDS (GB)"
  type        = number
  default     = 1000
}

variable "db_max_allocated_storage" {
  description = "Maximum storage allocation for RDS (GB)"
  type        = number
  default     = 5000
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "datnest"
}

variable "db_username" {
  description = "Database master username"
  type        = string
  default     = "datnest_admin"
}

variable "db_password" {
  description = "Database master password"
  type        = string
  sensitive   = true
}

# S3 Configuration
variable "s3_bucket_prefix" {
  description = "Prefix for S3 bucket names"
  type        = string
  default     = "datnest-core"
}

# Lambda Configuration
variable "lambda_runtime" {
  description = "Lambda runtime version"
  type        = string
  default     = "python3.11"
}

variable "lambda_timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 900  # 15 minutes for large TSV processing
}

variable "lambda_memory_size" {
  description = "Lambda function memory size in MB"
  type        = number
  default     = 3008  # Maximum for high-performance processing
}

# API Gateway Configuration
variable "api_stage_name" {
  description = "API Gateway stage name"
  type        = string
  default     = "v1"
}

# Monitoring Configuration
variable "enable_cloudwatch_logs" {
  description = "Enable CloudWatch logs for Lambda functions"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "CloudWatch log retention period in days"
  type        = number
  default     = 30
}

# Security Configuration
variable "allowed_cidr_blocks" {
  description = "CIDR blocks allowed to access the API"
  type        = list(string)
  default     = ["0.0.0.0/0"]  # Restrict in production
}

# Backup Configuration
variable "backup_retention_period" {
  description = "Database backup retention period in days"
  type        = number
  default     = 7
}

variable "backup_window" {
  description = "Preferred backup window"
  type        = string
  default     = "03:00-04:00"
}

variable "maintenance_window" {
  description = "Preferred maintenance window"
  type        = string
  default     = "sun:04:00-sun:05:00"
}

# Auto Scaling Configuration
variable "min_capacity" {
  description = "Minimum Aurora capacity units"
  type        = number
  default     = 2
}

variable "max_capacity" {
  description = "Maximum Aurora capacity units"
  type        = number
  default     = 64
}

# Tags
variable "additional_tags" {
  description = "Additional tags to apply to resources"
  type        = map(string)
  default     = {}
} 