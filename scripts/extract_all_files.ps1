# DataNest File Extraction Script
# Extracts all ZIP files from downloaded-zip to extracted-tsv
# Runs multiple extractions in parallel for speed

param(
    [int]$MaxJobs = 4  # Number of parallel extraction jobs
)

Write-Host "🚀 DataNest File Extraction Starting..." -ForegroundColor Green
Write-Host "📁 Extracting ZIP files with $MaxJobs parallel jobs" -ForegroundColor Cyan

# Paths
$DownloadedZipPath = "C:\DataNest-TSV-Files\downloaded-zip"
$ExtractedTsvPath = "C:\DataNest-TSV-Files\extracted-tsv"

# Get all ZIP files
$ZipFiles = Get-ChildItem -Path $DownloadedZipPath -Filter "*.zip" | Sort-Object Name

Write-Host "📋 Found $($ZipFiles.Count) ZIP files to extract" -ForegroundColor Yellow

# Track progress
$TotalFiles = $ZipFiles.Count
$CompletedFiles = 0
$StartTime = Get-Date

# Extract files in parallel batches
$JobBatches = @()
for ($i = 0; $i -lt $ZipFiles.Count; $i += $MaxJobs) {
    $Batch = $ZipFiles[$i..([Math]::Min($i + $MaxJobs - 1, $ZipFiles.Count - 1))]
    $JobBatches += ,@($Batch)
}

Write-Host "🔄 Processing $($JobBatches.Count) batches of extractions..." -ForegroundColor Cyan

foreach ($Batch in $JobBatches) {
    $Jobs = @()
    
    # Start extraction jobs for this batch
    foreach ($ZipFile in $Batch) {
        $JobName = "Extract_$($ZipFile.BaseName)"
        $ScriptBlock = {
            param($ZipPath, $ExtractPath, $FileName)
            
            try {
                $StartTime = Get-Date
                Expand-Archive -Path $ZipPath -DestinationPath $ExtractPath -Force
                $EndTime = Get-Date
                $Duration = ($EndTime - $StartTime).TotalSeconds
                
                # Get extracted file size
                $ExtractedFile = Join-Path $ExtractPath ($FileName -replace '\.zip$', '.TSV')
                if (Test-Path $ExtractedFile) {
                    $SizeGB = (Get-Item $ExtractedFile).Length / 1GB
                    return @{
                        Success = $true
                        FileName = $FileName
                        Duration = $Duration
                        SizeGB = [Math]::Round($SizeGB, 2)
                        Message = "✅ Extracted successfully"
                    }
                } else {
                    return @{
                        Success = $false
                        FileName = $FileName
                        Duration = $Duration
                        Message = "❌ Extraction failed - file not found"
                    }
                }
            }
            catch {
                return @{
                    Success = $false
                    FileName = $FileName
                    Duration = 0
                    Message = "❌ Extraction error: $($_.Exception.Message)"
                }
            }
        }
        
        $Job = Start-Job -Name $JobName -ScriptBlock $ScriptBlock -ArgumentList $ZipFile.FullName, $ExtractedTsvPath, $ZipFile.Name
        $Jobs += $Job
        
        Write-Host "  🔧 Started extraction: $($ZipFile.Name)" -ForegroundColor Gray
    }
    
    # Wait for batch to complete and show results
    Write-Host "⏳ Waiting for batch to complete..." -ForegroundColor Yellow
    
    $Results = @()
    foreach ($Job in $Jobs) {
        $Result = Receive-Job -Job $Job -Wait
        $Results += $Result
        Remove-Job -Job $Job
        
        $CompletedFiles++
        $OverallElapsed = (Get-Date) - $StartTime
        $OverallRate = $CompletedFiles / $OverallElapsed.TotalMinutes
        $ETA = ($TotalFiles - $CompletedFiles) / $OverallRate
        
        if ($Result.Success) {
            Write-Host "  ✅ $($Result.FileName): $($Result.SizeGB) GB in $([Math]::Round($Result.Duration, 1))s" -ForegroundColor Green
        } else {
            Write-Host "  ❌ $($Result.FileName): $($Result.Message)" -ForegroundColor Red
        }
        
        Write-Host "  📊 Progress: $CompletedFiles/$TotalFiles ($([Math]::Round(($CompletedFiles/$TotalFiles)*100, 1))%) - ETA: $([Math]::Round($ETA, 1)) min" -ForegroundColor Cyan
    }
    
    Write-Host "" # Empty line between batches
}

# Final summary
$TotalElapsed = (Get-Date) - $StartTime
$SuccessfulExtractions = $Results | Where-Object { $_.Success } | Measure-Object | Select-Object -ExpandProperty Count
$FailedExtractions = $Results | Where-Object { -not $_.Success } | Measure-Object | Select-Object -ExpandProperty Count

Write-Host "🎉 EXTRACTION COMPLETE!" -ForegroundColor Green
Write-Host "  📊 Total files: $TotalFiles" -ForegroundColor White
Write-Host "  ✅ Successful: $SuccessfulExtractions" -ForegroundColor Green
Write-Host "  ❌ Failed: $FailedExtractions" -ForegroundColor Red
Write-Host "  ⏱️  Total time: $([Math]::Round($TotalElapsed.TotalMinutes, 1)) minutes" -ForegroundColor White

# Show extracted files summary
Write-Host "📁 Extracted TSV files:" -ForegroundColor Cyan
$ExtractedFiles = Get-ChildItem -Path $ExtractedTsvPath -Filter "*.TSV" | Sort-Object Name
$TotalSizeGB = ($ExtractedFiles | Measure-Object -Property Length -Sum).Sum / 1GB

foreach ($File in $ExtractedFiles) {
    $SizeGB = [Math]::Round($File.Length / 1GB, 2)
    Write-Host "  📄 $($File.Name): $SizeGB GB" -ForegroundColor Gray
}

Write-Host "  📊 Total extracted: $($ExtractedFiles.Count) files, $([Math]::Round($TotalSizeGB, 1)) GB" -ForegroundColor Yellow

if ($FailedExtractions -eq 0) {
    Write-Host "🚀 Ready for parallel loading!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Some extractions failed. Check above for details." -ForegroundColor Yellow
} 