# RDS PostgreSQL Database for DatNest Core Platform
# Optimized for 150M+ property records with high performance

# DB subnet group
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnet-group"
  subnet_ids = aws_subnet.private[*].id

  tags = {
    Name = "${var.project_name}-db-subnet-group"
  }
}

# Security group for RDS
resource "aws_security_group" "rds" {
  name        = "${var.project_name}-rds-sg"
  description = "Security group for RDS PostgreSQL"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
    description = "PostgreSQL access from VPC"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = {
    Name = "${var.project_name}-rds-sg"
  }
}

# RDS parameter group for PostgreSQL optimization
resource "aws_db_parameter_group" "main" {
  family = "postgres14"
  name   = "${var.project_name}-postgres-params"

  # Optimize for large dataset performance
  parameter {
    name  = "log_min_duration_statement"
    value = "1000"  # Log queries taking more than 1 second
  }

  parameter {
    name  = "work_mem"
    value = "32768"  # 32MB for complex queries
  }

  parameter {
    name  = "maintenance_work_mem"
    value = "2097152"  # 2GB for maintenance operations
  }

  parameter {
    name  = "effective_cache_size"
    value = "12582912"  # 12GB - estimate of OS cache
  }

  parameter {
    name  = "random_page_cost"
    value = "1.1"  # Optimized for SSD storage
  }

  parameter {
    name  = "checkpoint_completion_target"
    value = "0.9"
  }

  parameter {
    name  = "default_statistics_target"
    value = "100"
  }

  tags = {
    Name = "${var.project_name}-postgres-params"
  }
}

# RDS instance
resource "aws_db_instance" "main" {
  identifier     = "${var.project_name}-postgres"
  engine         = "postgres"
  engine_version = "14.13"
  instance_class = var.db_instance_class

  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password
  port     = 5432

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  parameter_group_name   = aws_db_parameter_group.main.name

  # Backup configuration
  backup_retention_period = var.backup_retention_period
  backup_window          = var.backup_window
  maintenance_window     = var.maintenance_window

  # Monitoring
  monitoring_interval = 60
  monitoring_role_arn = aws_iam_role.rds_monitoring.arn

  # Performance Insights
  performance_insights_enabled = true
  performance_insights_retention_period = 7

  # Deletion protection
  deletion_protection = true
  skip_final_snapshot = false
  final_snapshot_identifier = "${var.project_name}-final-snapshot-${formatdate("YYYY-MM-DD-hhmm", timestamp())}"

  # Multi-AZ for high availability
  multi_az = true

  # Enable auto minor version upgrade
  auto_minor_version_upgrade = true

  tags = {
    Name = "${var.project_name}-postgres"
    Environment = var.environment
    Purpose = "Primary property database"
  }
}

# IAM role for RDS monitoring
resource "aws_iam_role" "rds_monitoring" {
  name = "${var.project_name}-rds-monitoring-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  role       = aws_iam_role.rds_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# RDS Proxy for connection pooling (important for Lambda)
resource "aws_db_proxy" "main" {
  name                   = "${var.project_name}-db-proxy"
  engine_family          = "POSTGRESQL"
  auth {
    auth_scheme = "SECRETS"
    secret_arn  = aws_secretsmanager_secret.db_credentials.arn
  }

  role_arn               = aws_iam_role.db_proxy.arn
  vpc_subnet_ids         = aws_subnet.private[*].id
  require_tls            = true

  tags = {
    Name = "${var.project_name}-db-proxy"
  }
}

# RDS Proxy target
resource "aws_db_proxy_default_target_group" "main" {
  db_proxy_name = aws_db_proxy.main.name

  connection_pool_config {
    connection_borrow_timeout    = 120
    max_connections_percent      = 100
    max_idle_connections_percent = 50
  }
}

resource "aws_db_proxy_target" "main" {
  db_instance_identifier = aws_db_instance.main.identifier
  db_proxy_name          = aws_db_proxy.main.name
  target_group_name      = aws_db_proxy_default_target_group.main.name
}

# Secrets Manager for database credentials
resource "aws_secretsmanager_secret" "db_credentials" {
  name        = "${var.project_name}/db/credentials"
  description = "Database credentials for DatNest Core Platform"
}

resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    username = var.db_username
    password = var.db_password
    engine   = "postgres"
    host     = aws_db_instance.main.address
    port     = 5432
    dbname   = var.db_name
  })
}

# IAM role for RDS Proxy
resource "aws_iam_role" "db_proxy" {
  name = "${var.project_name}-db-proxy-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "rds.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "db_proxy" {
  name = "${var.project_name}-db-proxy-policy"
  role = aws_iam_role.db_proxy.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = aws_secretsmanager_secret.db_credentials.arn
      }
    ]
  })
} 