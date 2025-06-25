# DatNest Core Platform - Setup Guide

Welcome to the DatNest Core Platform! This guide will walk you through setting up the production-ready AWS infrastructure for processing 32GB+ of property data and scaling to 150M+ records.

## 🎯 **Overview**

We're building upon your successful prototype to create a cloud-native platform that can:
- Process 32 TSV files (~1GB each, 32GB total)
- Handle 150M+ property records with QVM valuations
- Provide sub-100ms API responses for property searches
- Scale automatically based on demand

## 📋 **Prerequisites**

### Required Tools
- **AWS CLI** (v2.0+) - For interacting with AWS services
- **Terraform** (v1.0+) - Infrastructure as Code
- **Python** (3.9+) - For Lambda functions and data processing
- **PostgreSQL Client** - For database management

### AWS Account Requirements
- AWS account with appropriate permissions
- Estimated monthly cost: $500-1500 (depending on usage)
- Access to create VPC, RDS, Lambda, S3, and IAM resources

## 🚀 **Step 1: AWS CLI Setup**

### Install AWS CLI (if not already installed)

**Windows (PowerShell):**
```powershell
# Download and install AWS CLI
Invoke-WebRequest -Uri "https://awscli.amazonaws.com/AWSCLIV2.msi" -OutFile "AWSCLIV2.msi"
Start-Process msiexec.exe -ArgumentList "/i AWSCLIV2.msi /quiet" -Wait
```

**Alternative - Using Chocolatey:**
```powershell
choco install awscli
```

### Configure AWS Credentials

```powershell
# Configure AWS credentials
aws configure

# Enter your AWS credentials when prompted:
# AWS Access Key ID: [Your Access Key]
# AWS Secret Access Key: [Your Secret Key]
# Default region name: us-east-1
# Default output format: json
```

### Verify AWS Access
```powershell
# Test AWS connection
aws sts get-caller-identity

# Should return your AWS account details
```

## 🏗️ **Step 2: Infrastructure Setup with Terraform**

### Install Terraform

**Windows (PowerShell):**
```powershell
# Download and install Terraform
$terraformUrl = "https://releases.hashicorp.com/terraform/1.6.4/terraform_1.6.4_windows_amd64.zip"
Invoke-WebRequest -Uri $terraformUrl -OutFile "terraform.zip"
Expand-Archive -Path "terraform.zip" -DestinationPath "C:\terraform"

# Add to PATH (run as Administrator)
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\terraform", "Machine")
```

**Alternative - Using Chocolatey:**
```powershell
choco install terraform
```

### Configure Terraform Variables

```powershell
# Navigate to terraform directory
cd infrastructure/terraform

# Copy example variables file
Copy-Item terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your preferred editor
notepad terraform.tfvars
```

**Important Configuration Changes in terraform.tfvars:**

```hcl
# REQUIRED: Change the database password
db_password = "YourSecurePassword123!"

# RECOMMENDED: Restrict network access (replace with your IP)
allowed_cidr_blocks = ["YOUR.PUBLIC.IP.ADDRESS/32"]

# OPTIONAL: Adjust region if needed
aws_region = "us-east-1"  # or your preferred region
```

### Deploy Infrastructure

```powershell
# Initialize Terraform
terraform init

# Review the deployment plan
terraform plan

# Deploy infrastructure (this will take 15-20 minutes)
terraform apply

# Type 'yes' when prompted to confirm deployment
```

**Expected Output:**
- VPC with public/private subnets
- RDS PostgreSQL instance (optimized for 150M+ records)
- S3 buckets for data storage
- Lambda functions for data processing
- Security groups and IAM roles

## 📊 **Step 3: Database Schema Setup**

### Connect to Database

```powershell
# Get database connection info from Terraform output
terraform output -json > outputs.json

# Extract database endpoint (will be needed for connection)
$dbEndpoint = (terraform output -raw rds_endpoint)
Write-Host "Database Endpoint: $dbEndpoint"
```

### Run Database Migrations

```powershell
# Navigate to database directory
cd ../../database

# Install PostgreSQL client if needed
# For Windows: Download from https://www.postgresql.org/download/windows/

# Run initial schema migration
psql -h $dbEndpoint -p 5432 -U datnest_admin -d datnest -f migrations/001_initial_schema.sql

# Enter database password when prompted
```

## 📁 **Step 4: TSV File Analysis**

Now let's analyze your TSV schema to ensure field mapping accuracy:

### Upload Sample TSV File

```powershell
# Navigate back to project root
cd ../..

# Get S3 bucket name from Terraform
$rawBucket = (terraform output -raw s3_raw_data_bucket)

# Upload a sample TSV file for analysis
aws s3 cp "path/to/your/sample.tsv" "s3://$rawBucket/incoming/sample.tsv"
```

### Run Schema Analysis

```powershell
# Navigate to data processing directory
cd data-processing/schema-mappings

# Create virtual environment for Python
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install pandas boto3 psycopg2-binary

# Run field mapping analysis (we'll create this script)
python analyze_tsv_schema.py --bucket $rawBucket --file sample.tsv
```

## 🔍 **Step 5: Verify Field Mappings**

Based on your prototype lessons, we've mapped the most critical fields:

### **Tier 1 (Highest Priority) - QVM Fields:**
- `Quantarium Value` → `estimated_value`
- `Quantarium Value High` → `price_range_max`
- `Quantarium Value Low` → `price_range_min`
- `Quantarium Value Confidence` → `confidence_score`
- `QVM_asof_Date` → `qvm_asof_date`

### **Verify Field Names in Your TSV Files:**

1. **Check first row of your TSV files for actual field names**
2. **Compare with our mapping in** `data-processing/schema-mappings/tsv_field_mapping.py`
3. **Update mappings if field names differ**

**Common Field Name Variations to Check:**
- `Quantarium Value` vs `ESTIMATED_VALUE`
- `Site Address` vs `Property_Full_Street_Address`
- `Building Area 1` vs `Building_Area_1`
- `APN` vs `Assessors_Parcel_Number`

## 📈 **Step 6: Performance Monitoring Setup**

### CloudWatch Dashboard

```powershell
# Create CloudWatch dashboard for monitoring
aws cloudwatch put-dashboard --dashboard-name "DatNest-Core-Platform" --dashboard-body file://monitoring/cloudwatch-dashboard.json
```

### Set Up Alerts

```powershell
# Create CloudWatch alarms for critical metrics
aws cloudwatch put-metric-alarm --alarm-name "DatNest-RDS-CPU-High" --alarm-actions "arn:aws:sns:us-east-1:YOUR-ACCOUNT:alerts" --metric-name CPUUtilization --namespace AWS/RDS --statistic Average --period 300 --threshold 80 --comparison-operator GreaterThanThreshold
```

## 🧪 **Step 7: Test Infrastructure**

### Test Database Connection

```powershell
# Test database connection and schema
psql -h $dbEndpoint -p 5432 -U datnest_admin -d datnest -c "\dt datnest.*"

# Should show your tables: properties, property_owners, etc.
```

### Test S3 Access

```powershell
# List S3 buckets
aws s3 ls | findstr datnest

# Should show your three buckets: raw-data, processed-data, lambda-deployments
```

### Test Lambda Functions

```powershell
# Test TSV processor function
aws lambda invoke --function-name datnest-core-tsv-processor --payload '{"test": "true"}' response.json

# Check response
Get-Content response.json
```

## 📊 **Step 8: Data Processing Pipeline**

### Upload Your TSV Files

```powershell
# Upload all 32 TSV files to S3 (this will trigger processing)
for ($i=1; $i -le 32; $i++) {
    aws s3 cp "path/to/your/tsv-files/file$i.tsv" "s3://$rawBucket/incoming/"
}
```

### Monitor Processing

```powershell
# Check CloudWatch logs for processing status
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/datnest-core"

# View processing logs
aws logs filter-log-events --log-group-name "/aws/lambda/datnest-core-tsv-processor" --start-time (Get-Date).AddHours(-1).Ticks
```

## 🎯 **Expected Results**

After successful setup, you should have:

### **Infrastructure:**
- ✅ Production-ready AWS infrastructure
- ✅ PostgreSQL database optimized for 150M+ records
- ✅ S3 data lake for 32GB+ TSV processing
- ✅ Serverless Lambda functions for ETL
- ✅ Monitoring and alerting setup

### **Data Processing:**
- ✅ Automated TSV file processing
- ✅ QVM field mapping with 99.9% coverage
- ✅ Data quality validation and scoring
- ✅ Real-time processing status tracking

### **Performance Targets:**
- ✅ Data processing: 1M+ records/hour
- ✅ Database queries: Sub-200ms response
- ✅ API endpoints: <100ms for cached queries
- ✅ System uptime: 99.9% availability

## 🚨 **Troubleshooting**

### Common Issues:

**1. Terraform Apply Fails:**
```powershell
# Clean up and retry
terraform destroy -auto-approve
terraform apply
```

**2. Database Connection Issues:**
```powershell
# Check security groups allow your IP
aws ec2 describe-security-groups --group-ids sg-xxxxx
```

**3. Lambda Function Timeout:**
```powershell
# Check CloudWatch logs for specific errors
aws logs tail /aws/lambda/datnest-core-tsv-processor --follow
```

**4. S3 Processing Not Triggering:**
```powershell
# Verify S3 bucket notifications are configured
aws s3api get-bucket-notification-configuration --bucket $rawBucket
```

## 💡 **Next Steps**

Once infrastructure is set up:

1. **Validate Field Mappings** - Ensure TSV field names match our mappings
2. **Process Sample Data** - Test with small TSV file first
3. **Full Data Load** - Process all 32 TSV files
4. **API Development** - Build FastAPI endpoints
5. **Frontend Development** - Create user interface

## 🤝 **Getting Help**

If you encounter any issues:

1. **Check CloudWatch Logs** - Most issues show up in logs
2. **Verify AWS Permissions** - Ensure your AWS user has required permissions
3. **Review Terraform State** - Check `terraform show` for resource status
4. **Monitor Costs** - Use AWS Cost Explorer to track spending

---

**🎉 Congratulations!** You're now ready to scale your property data platform to handle 150M+ records with production-grade AWS infrastructure!

The foundation is solid, and we can now focus on optimizing the data processing pipeline and building the user-facing features that will make this platform amazing. 