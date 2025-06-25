# DatNest Core Platform - Quick Start Script
# PowerShell script for rapid AWS infrastructure deployment

param(
    [string]$Region = "us-east-1",
    [string]$ProjectName = "datnest-core",
    [string]$DBPassword,
    [switch]$SkipValidation,
    [switch]$DestroyInfrastructure
)

# Colors for output
$Red = [System.ConsoleColor]::Red
$Green = [System.ConsoleColor]::Green
$Yellow = [System.ConsoleColor]::Yellow
$Blue = [System.ConsoleColor]::Blue

function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    } else {
        $input | Write-Output
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Header {
    param([string]$Message)
    Write-ColorOutput $Blue ("=" * 80)
    Write-ColorOutput $Blue "🏗️  DATNEST CORE PLATFORM - $Message"
    Write-ColorOutput $Blue ("=" * 80)
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput $Green "✅ $Message"
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput $Yellow "⚠️  $Message"
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput $Red "❌ $Message"
}

function Test-Command {
    param([string]$Command, [string]$Name)
    
    if (Get-Command $Command -ErrorAction SilentlyContinue) {
        Write-Success "$Name is installed"
        return $true
    } else {
        Write-Error "$Name is not installed"
        return $false
    }
}

function Install-Prerequisites {
    Write-Header "CHECKING PREREQUISITES"
    
    $allInstalled = $true
    
    # Check AWS CLI
    if (-not (Test-Command "aws" "AWS CLI")) {
        Write-Warning "Installing AWS CLI..."
        try {
            Invoke-WebRequest -Uri "https://awscli.amazonaws.com/AWSCLIV2.msi" -OutFile "AWSCLIV2.msi"
            Start-Process msiexec.exe -ArgumentList "/i AWSCLIV2.msi /quiet" -Wait
            Remove-Item "AWSCLIV2.msi"
            Write-Success "AWS CLI installed successfully"
        } catch {
            Write-Error "Failed to install AWS CLI: $_"
            $allInstalled = $false
        }
    }
    
    # Check Terraform
    if (-not (Test-Command "terraform" "Terraform")) {
        Write-Warning "Installing Terraform..."
        try {
            if (Get-Command "choco" -ErrorAction SilentlyContinue) {
                choco install terraform -y
            } else {
                Write-Error "Please install Terraform manually from https://www.terraform.io/downloads.html"
                $allInstalled = $false
            }
        } catch {
            Write-Error "Failed to install Terraform: $_"
            $allInstalled = $false
        }
    }
    
    # Check Python
    if (-not (Test-Command "python" "Python")) {
        Write-Error "Python is required. Please install Python 3.9+ from https://www.python.org/downloads/"
        $allInstalled = $false
    }
    
    return $allInstalled
}

function Test-AWSCredentials {
    Write-Header "VALIDATING AWS CREDENTIALS"
    
    try {
        $identity = aws sts get-caller-identity --output json | ConvertFrom-Json
        Write-Success "AWS credentials are valid"
        Write-Output "   Account: $($identity.Account)"
        Write-Output "   User/Role: $($identity.Arn)"
        return $true
    } catch {
        Write-Error "AWS credentials are not configured or invalid"
        Write-Warning "Please run: aws configure"
        return $false
    }
}

function Deploy-Infrastructure {
    Write-Header "DEPLOYING AWS INFRASTRUCTURE"
    
    # Navigate to terraform directory
    Push-Location "infrastructure/terraform"
    
    try {
        # Create terraform.tfvars if it doesn't exist
        if (-not (Test-Path "terraform.tfvars")) {
            Write-Warning "Creating terraform.tfvars from template..."
            Copy-Item "terraform.tfvars.example" "terraform.tfvars"
            
            # Update with provided values
            $tfvars = Get-Content "terraform.tfvars"
            if ($Region) {
                $tfvars = $tfvars -replace 'aws_region\s*=\s*"[^"]*"', "aws_region = `"$Region`""
            }
            if ($ProjectName) {
                $tfvars = $tfvars -replace 'project_name\s*=\s*"[^"]*"', "project_name = `"$ProjectName`""
            }
            if ($DBPassword) {
                $tfvars = $tfvars -replace 'db_password\s*=\s*"[^"]*"', "db_password = `"$DBPassword`""
            }
            $tfvars | Set-Content "terraform.tfvars"
            
            Write-Warning "⚠️  IMPORTANT: Please edit terraform.tfvars to:"
            Write-Output "   1. Set a secure database password"
            Write-Output "   2. Restrict allowed_cidr_blocks to your IP"
            Write-Output ""
            Write-Output "Press Enter to continue after editing, or Ctrl+C to abort..."
            Read-Host
        }
        
        # Initialize Terraform
        Write-Output "Initializing Terraform..."
        terraform init
        if ($LASTEXITCODE -ne 0) {
            throw "Terraform init failed"
        }
        
        # Plan deployment
        Write-Output "Planning deployment..."
        terraform plan -out=tfplan
        if ($LASTEXITCODE -ne 0) {
            throw "Terraform plan failed"
        }
        
        # Apply deployment
        Write-Output "Deploying infrastructure (this may take 15-20 minutes)..."
        terraform apply tfplan
        if ($LASTEXITCODE -ne 0) {
            throw "Terraform apply failed"
        }
        
        Write-Success "Infrastructure deployed successfully!"
        
        # Output important information
        Write-Output "`nIMPORTANT OUTPUTS:"
        terraform output
        
    } catch {
        Write-Error "Infrastructure deployment failed: $_"
        return $false
    } finally {
        Pop-Location
    }
    
    return $true
}

function Setup-Database {
    Write-Header "SETTING UP DATABASE SCHEMA"
    
    try {
        # Get database endpoint
        Push-Location "infrastructure/terraform"
        $dbEndpoint = terraform output -raw rds_endpoint
        Pop-Location
        
        if (-not $dbEndpoint) {
            throw "Could not get database endpoint from Terraform"
        }
        
        Write-Output "Database endpoint: $dbEndpoint"
        
        # Check if psql is available
        if (-not (Get-Command "psql" -ErrorAction SilentlyContinue)) {
            Write-Warning "PostgreSQL client (psql) not found"
            Write-Output "Please install PostgreSQL client and run manually:"
            Write-Output "psql -h $dbEndpoint -p 5432 -U datnest_admin -d datnest -f database/migrations/001_initial_schema.sql"
            return $false
        }
        
        # Run migrations
        Write-Output "Running database migrations..."
        $env:PGPASSWORD = $DBPassword
        psql -h $dbEndpoint -p 5432 -U datnest_admin -d datnest -f "database/migrations/001_initial_schema.sql"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Database schema created successfully!"
        } else {
            Write-Error "Database migration failed"
            return $false
        }
        
    } catch {
        Write-Error "Database setup failed: $_"
        return $false
    }
    
    return $true
}

function Test-Infrastructure {
    Write-Header "TESTING INFRASTRUCTURE"
    
    try {
        Push-Location "infrastructure/terraform"
        
        # Test S3 buckets
        $rawBucket = terraform output -raw s3_raw_data_bucket
        $processedBucket = terraform output -raw s3_processed_data_bucket
        
        aws s3 ls "s3://$rawBucket" > $null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "S3 raw data bucket accessible"
        } else {
            Write-Error "S3 raw data bucket not accessible"
        }
        
        aws s3 ls "s3://$processedBucket" > $null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "S3 processed data bucket accessible"
        } else {
            Write-Error "S3 processed data bucket not accessible"
        }
        
        # Test Lambda functions
        $tsvProcessor = terraform output -raw lambda_tsv_processor_function_name
        aws lambda get-function --function-name $tsvProcessor > $null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Lambda TSV processor function exists"
        } else {
            Write-Error "Lambda TSV processor function not found"
        }
        
        Pop-Location
        
    } catch {
        Write-Error "Infrastructure testing failed: $_"
        return $false
    }
    
    return $true
}

function Show-NextSteps {
    Write-Header "NEXT STEPS"
    
    Write-Output "🎉 Your DatNest Core Platform infrastructure is ready!"
    Write-Output ""
    Write-Output "To continue:"
    Write-Output ""
    Write-Output "1. ANALYZE YOUR TSV FILES:"
    Write-Output "   cd data-processing/schema-mappings"
    Write-Output "   python -m venv venv"
    Write-Output "   .\venv\Scripts\Activate.ps1"
    Write-Output "   pip install pandas boto3 psycopg2-binary"
    Write-Output "   python analyze_tsv_schema.py --local path/to/your/sample.tsv"
    Write-Output ""
    Write-Output "2. UPDATE FIELD MAPPINGS (if needed):"
    Write-Output "   Edit: data-processing/schema-mappings/tsv_field_mapping.py"
    Write-Output ""
    Write-Output "3. UPLOAD AND PROCESS TSV FILES:"
    Push-Location "infrastructure/terraform" -ErrorAction SilentlyContinue
    $rawBucket = terraform output -raw s3_raw_data_bucket 2>$null
    Pop-Location -ErrorAction SilentlyContinue
    Write-Output "   aws s3 cp your-file.tsv s3://$rawBucket/incoming/"
    Write-Output ""
    Write-Output "4. MONITOR PROCESSING:"
    Write-Output "   aws logs tail /aws/lambda/datnest-core-tsv-processor --follow"
    Write-Output ""
    Write-Output "5. BUILD API AND FRONTEND:"
    Write-Output "   cd api && python -m venv venv && pip install fastapi uvicorn"
    Write-Output "   cd frontend && npm install && npm run dev"
    Write-Output ""
    Write-ColorOutput $Green "🚀 Ready to scale to 150M+ property records!"
}

function Destroy-Infrastructure {
    Write-Header "DESTROYING INFRASTRUCTURE"
    
    Write-Warning "This will destroy ALL AWS resources created by this project!"
    Write-Output "Type 'yes' to confirm destruction:"
    $confirmation = Read-Host
    
    if ($confirmation -eq "yes") {
        Push-Location "infrastructure/terraform"
        terraform destroy -auto-approve
        Pop-Location
        Write-Success "Infrastructure destroyed"
    } else {
        Write-Output "Destruction cancelled"
    }
}

# Main execution
Write-Header "QUICK START DEPLOYMENT"

if ($DestroyInfrastructure) {
    Destroy-Infrastructure
    exit
}

if (-not $DBPassword) {
    Write-Output "Database password not provided. Please enter a secure password:"
    $DBPassword = Read-Host -AsSecureString "Database Password" | ConvertFrom-SecureString -AsPlainText
}

# Step 1: Prerequisites
if (-not $SkipValidation) {
    if (-not (Install-Prerequisites)) {
        Write-Error "Prerequisites check failed. Please install missing tools."
        exit 1
    }
    
    if (-not (Test-AWSCredentials)) {
        Write-Error "AWS credentials validation failed."
        exit 1
    }
}

# Step 2: Deploy Infrastructure
if (-not (Deploy-Infrastructure)) {
    Write-Error "Infrastructure deployment failed."
    exit 1
}

# Step 3: Setup Database
if (-not (Setup-Database)) {
    Write-Warning "Database setup failed, but infrastructure is deployed."
    Write-Output "You can set up the database manually later."
}

# Step 4: Test Infrastructure
if (-not (Test-Infrastructure)) {
    Write-Warning "Some infrastructure tests failed, but deployment completed."
}

# Step 5: Show next steps
Show-NextSteps

Write-Success "Quick start deployment completed!" 