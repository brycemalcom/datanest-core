# Bastion Host for Database Access

# Create key pair for SSH access
resource "aws_key_pair" "bastion_key" {
  key_name   = "datnest-bastion-key"
  public_key = file("~/.ssh/datnest_bastion.pub")
  
  tags = {
    Name        = "DataNest Bastion Key"
    Environment = "production"
    Project     = "datnest-core"
  }
}

# Security Group for Bastion Host
resource "aws_security_group" "bastion" {
  name_prefix = "datnest-bastion-"
  vpc_id      = aws_vpc.main.id
  description = "Security group for bastion host"

  # SSH access from anywhere (you can restrict to your IP if needed)
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "SSH access"
  }

  # All outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = {
    Name        = "DataNest Bastion Security Group"
    Environment = "production"
    Project     = "datnest-core"
  }
}

# Update RDS security group to allow bastion access
resource "aws_security_group_rule" "rds_from_bastion" {
  type                     = "ingress"
  from_port                = 5432
  to_port                  = 5432
  protocol                 = "tcp"
  source_security_group_id = aws_security_group.bastion.id
  security_group_id        = aws_security_group.rds.id
  description              = "PostgreSQL access from bastion host"
}

# Get latest Amazon Linux 2 AMI
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Bastion Host EC2 Instance
resource "aws_instance" "bastion" {
  ami                         = data.aws_ami.amazon_linux.id
  instance_type              = "t3.micro"
  key_name                   = aws_key_pair.bastion_key.key_name
  vpc_security_group_ids     = [aws_security_group.bastion.id]
  subnet_id                  = aws_subnet.public[0].id
  associate_public_ip_address = true

  # User data script to install PostgreSQL client
  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y postgresql15
              
              # Create a simple connection script
              cat > /home/ec2-user/connect_db.sh << 'SCRIPT'
#!/bin/bash
echo "Connecting to DataNest PostgreSQL Database..."
echo "Host: ${aws_db_instance.main.endpoint}"
echo "Database: ${aws_db_instance.main.db_name}"
echo "Username: ${aws_db_instance.main.username}"
echo ""
echo "Use this command to connect:"
echo "psql -h ${aws_db_instance.main.endpoint} -U ${aws_db_instance.main.username} -d ${aws_db_instance.main.db_name}"
SCRIPT
              chmod +x /home/ec2-user/connect_db.sh
              chown ec2-user:ec2-user /home/ec2-user/connect_db.sh
              EOF

  tags = {
    Name        = "DataNest Bastion Host"
    Environment = "production"
    Project     = "datnest-core" 
    Purpose     = "Database Access"
  }
}

# Elastic IP for bastion (optional but recommended)
resource "aws_eip" "bastion" {
  instance = aws_instance.bastion.id
  domain   = "vpc"

  tags = {
    Name        = "DataNest Bastion EIP"
    Environment = "production"
    Project     = "datnest-core"
  }
} 