# DataNest File Structure Setup Script
# Run this tonight to prepare for tomorrow's massive data loading

Write-Host "🏗️  Setting up DataNest file structure for massive loading..." -ForegroundColor Green

# Create main directory
$mainPath = "C:\DataNest-TSV-Files"
Write-Host "📁 Creating main directory: $mainPath"

if (-not (Test-Path $mainPath)) {
    New-Item -ItemType Directory -Path $mainPath -Force
    Write-Host "✅ Created: $mainPath" -ForegroundColor Green
} else {
    Write-Host "✅ Already exists: $mainPath" -ForegroundColor Yellow
}

# Create subdirectories
$subDirs = @(
    "downloaded-zip",
    "extracted-tsv", 
    "completed",
    "logs",
    "scripts"
)

foreach ($dir in $subDirs) {
    $fullPath = Join-Path $mainPath $dir
    if (-not (Test-Path $fullPath)) {
        New-Item -ItemType Directory -Path $fullPath -Force
        Write-Host "✅ Created: $fullPath" -ForegroundColor Green
    } else {
        Write-Host "✅ Already exists: $fullPath" -ForegroundColor Yellow
    }
}

# Check available disk space
Write-Host "`n💾 Checking disk space requirements..." -ForegroundColor Cyan

$drive = Get-WmiObject -Class Win32_LogicalDisk -Filter "DeviceID='C:'"
$freeSpaceGB = [math]::Round($drive.FreeSpace / 1GB, 2)
$requiredSpaceGB = 275

Write-Host "Available space on C: drive: $freeSpaceGB GB" -ForegroundColor White
Write-Host "Required space for loading: $requiredSpaceGB GB" -ForegroundColor White

if ($freeSpaceGB -ge $requiredSpaceGB) {
    Write-Host "✅ SUFFICIENT DISK SPACE AVAILABLE" -ForegroundColor Green
} else {
    Write-Host "⚠️  WARNING: Insufficient disk space!" -ForegroundColor Red
    Write-Host "   Need to free up: $([math]::Round($requiredSpaceGB - $freeSpaceGB, 2)) GB" -ForegroundColor Red
}

# Move existing TSV file if it exists
$existingTSV = "Quantarium_OpenLien_20250414_00001.TSV"
if (Test-Path $existingTSV) {
    $destination = Join-Path $mainPath "extracted-tsv\$existingTSV"
    Write-Host "`n📦 Moving existing TSV file to organized location..."
    Move-Item $existingTSV $destination -Force
    Write-Host "✅ Moved: $existingTSV → $destination" -ForegroundColor Green
}

# Create simple tracking file
$trackingFile = Join-Path $mainPath "logs\file_processing_tracker.txt"
$content = "DataNest File Processing Tracker`n"
$content += "Generated: $(Get-Date)`n"
$content += "Total Files: 32`n"
$content += "Expected Total Size: ~195 GB`n`n"
$content += "File 01: Already processed in sample (5,000 records)`n"
$content += "Files 02-32: Ready for parallel processing`n`n"
$content += "Notes:`n"
$content += "- Each file is approximately 6.1 GB uncompressed`n"
$content += "- Total dataset: ~160 million property records`n"
$content += "- QVM coverage expected: ~38.4%`n"

Set-Content -Path $trackingFile -Value $content
Write-Host "✅ Created tracking file: $trackingFile" -ForegroundColor Green

# Create README file
$readmeFile = Join-Path $mainPath "README.txt"
$readmeContent = "DataNest Massive Loading Project`n"
$readmeContent += "===============================`n"
$readmeContent += "Created: $(Get-Date)`n`n"
$readmeContent += "FOLDER STRUCTURE:`n"
$readmeContent += "downloaded-zip\     - ZIP files from FTP (32 files, ~32GB)`n"
$readmeContent += "extracted-tsv\      - Uncompressed TSV files (32 files, ~195GB)`n"  
$readmeContent += "completed\          - Successfully processed files`n"
$readmeContent += "logs\              - Processing logs and tracking`n"
$readmeContent += "scripts\           - Loading scripts and utilities`n`n"
$readmeContent += "EXPECTED RESULTS:`n"
$readmeContent += "- 160+ million property records loaded`n"
$readmeContent += "- 61+ million properties with QVM valuations`n"
$readmeContent += "- Database ready for API development`n"
$readmeContent += "- All temporary infrastructure automatically scaled back`n`n"
$readmeContent += "COST: ~500-1000 for temporary scaling (auto scale-down included)`n"
$readmeContent += "TIME: 12-24 hours total execution`n"

Set-Content -Path $readmeFile -Value $readmeContent
Write-Host "✅ Created README: $readmeFile" -ForegroundColor Green

Write-Host "`n🎯 SETUP COMPLETE!" -ForegroundColor Green
Write-Host "✅ File structure created" -ForegroundColor Green
Write-Host "✅ Tracking files generated" -ForegroundColor Green
Write-Host "✅ Disk space verified" -ForegroundColor Green

Write-Host "`n📋 TONIGHT'S CHECKLIST:" -ForegroundColor Cyan
Write-Host "1. Download 31 remaining ZIP files from FTP" -ForegroundColor White
Write-Host "   → Save to: C:\DataNest-TSV-Files\downloaded-zip\" -ForegroundColor Gray
Write-Host "2. Extract all ZIP files to TSV format" -ForegroundColor White
Write-Host "   → Save to: C:\DataNest-TSV-Files\extracted-tsv\" -ForegroundColor Gray
Write-Host "3. Verify all 32 TSV files are ~6.1GB each" -ForegroundColor White
Write-Host "4. Get good sleep for tomorrow's marathon! 😴" -ForegroundColor White

Write-Host "`n🚀 Tomorrow we load 160+ million records and make DataNest history!" -ForegroundColor Green 