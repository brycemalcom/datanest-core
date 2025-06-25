# DataNest SSH Tunnel Setup
# Establishes secure tunnel to RDS via bastion host

Write-Host "[SSH] Setting up SSH tunnel to database..." -ForegroundColor Green

$BastionIP = "44.216.213.56"
$LocalPort = 15432
$RDSHost = "datnest-core-postgres.c6j8ogmi4mxb.us-east-1.rds.amazonaws.com"
$RDSPort = 5432

# Check if tunnel already exists
$ExistingTunnel = Get-Process -Name "ssh" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*15432*" }

if ($ExistingTunnel) {
    Write-Host "[WARNING] SSH tunnel already running (PID: $($ExistingTunnel.Id))" -ForegroundColor Yellow
    Write-Host "   If you need to restart, kill the process first:" -ForegroundColor Yellow
    Write-Host "   Stop-Process -Id $($ExistingTunnel.Id)" -ForegroundColor Gray
} else {
    Write-Host "[STARTING] SSH tunnel..." -ForegroundColor Cyan
    Write-Host "   Local Port: $LocalPort" -ForegroundColor Gray
    Write-Host "   Bastion: $BastionIP" -ForegroundColor Gray
    Write-Host "   RDS: ${RDSHost}:${RDSPort}" -ForegroundColor Gray
    
    # Start SSH tunnel in background
    $SSHArgs = @(
        "-i", "~/.ssh/datnest_bastion",
        "-L", "${LocalPort}:${RDSHost}:${RDSPort}",
        "-N",
        "-f",
        "ec2-user@$BastionIP"
    )
    
    try {
        Start-Process -FilePath "ssh" -ArgumentList $SSHArgs -WindowStyle Hidden
        Start-Sleep -Seconds 3
        
        # Test if tunnel is working
        $TestConnection = Test-NetConnection -ComputerName "localhost" -Port $LocalPort -WarningAction SilentlyContinue
        
        if ($TestConnection.TcpTestSucceeded) {
            Write-Host "[SUCCESS] SSH tunnel established successfully!" -ForegroundColor Green
            Write-Host "   Database accessible at localhost:$LocalPort" -ForegroundColor Green
        } else {
            Write-Host "[ERROR] SSH tunnel failed to establish" -ForegroundColor Red
            Write-Host "   Check SSH key and bastion host connectivity" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "[ERROR] SSH tunnel setup failed: $($_.Exception.Message)" -ForegroundColor Red
    }
} 