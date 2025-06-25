# Simple batch extractor - Extract 4 files at a time
Write-Host "🚀 Starting batch extraction..." -ForegroundColor Green

$ZipPath = "C:\DataNest-TSV-Files\downloaded-zip"
$ExtractPath = "C:\DataNest-TSV-Files\extracted-tsv"

# Get files that need extraction (skip already extracted)
$AllZips = Get-ChildItem -Path $ZipPath -Filter "*.zip" | Sort-Object Name
$Extracted = Get-ChildItem -Path $ExtractPath -Filter "*.TSV" | ForEach-Object { $_.Name.Replace('.TSV', '.zip') }
$ToExtract = $AllZips | Where-Object { $_.Name -notin $Extracted }

Write-Host "📋 Found $($ToExtract.Count) files to extract" -ForegroundColor Yellow

# Extract in batches of 4
$BatchSize = 4
for ($i = 0; $i -lt $ToExtract.Count; $i += $BatchSize) {
    $Batch = $ToExtract[$i..([Math]::Min($i + $BatchSize - 1, $ToExtract.Count - 1))]
    $Jobs = @()
    
    Write-Host "🔄 Starting batch $([Math]::Floor($i/$BatchSize) + 1)..." -ForegroundColor Cyan
    
    foreach ($File in $Batch) {
        $Job = Start-Job -ScriptBlock {
            param($ZipFile, $ExtractPath)
            $StartTime = Get-Date
            Expand-Archive -Path $ZipFile -DestinationPath $ExtractPath -Force
            $Duration = (Get-Date) - $StartTime
            return @{
                File = Split-Path $ZipFile -Leaf
                Duration = $Duration.TotalSeconds
            }
        } -ArgumentList $File.FullName, $ExtractPath
        
        $Jobs += $Job
        Write-Host "  🔧 Started: $($File.Name)" -ForegroundColor Gray
    }
    
    # Wait for batch
    $Results = $Jobs | Receive-Job -Wait
    $Jobs | Remove-Job
    
    foreach ($Result in $Results) {
        Write-Host "  ✅ $($Result.File): $([Math]::Round($Result.Duration, 1))s" -ForegroundColor Green
    }
    
    Write-Host ""
}

Write-Host "🎉 Batch extraction complete!" -ForegroundColor Green 