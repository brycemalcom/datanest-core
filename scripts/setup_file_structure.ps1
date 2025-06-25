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

# Create file tracking template
$trackingFile = Join-Path $mainPath "logs\file_processing_tracker.txt"
$trackingContent = @"
DataNest File Processing Tracker
Generated: $(Get-Date)
Total Files: 32
Expected Total Size: ~195 GB

File Status Tracking:
=====================
- File 01: Quantarium_OpenLien_20250414_00001.TSV (Already processed in sample)
- File 02: Quantarium_OpenLien_20250414_00002.TSV
- File 03: Quantarium_OpenLien_20250414_00003.TSV
- File 04: Quantarium_OpenLien_20250414_00004.TSV
- File 05: Quantarium_OpenLien_20250414_00005.TSV
- File 06: Quantarium_OpenLien_20250414_00006.TSV
- File 07: Quantarium_OpenLien_20250414_00007.TSV
- File 08: Quantarium_OpenLien_20250414_00008.TSV
- File 09: Quantarium_OpenLien_20250414_00009.TSV
- File 10: Quantarium_OpenLien_20250414_00010.TSV
- File 11: Quantarium_OpenLien_20250414_00011.TSV
- File 12: Quantarium_OpenLien_20250414_00012.TSV
- File 13: Quantarium_OpenLien_20250414_00013.TSV
- File 14: Quantarium_OpenLien_20250414_00014.TSV
- File 15: Quantarium_OpenLien_20250414_00015.TSV
- File 16: Quantarium_OpenLien_20250414_00016.TSV
- File 17: Quantarium_OpenLien_20250414_00017.TSV
- File 18: Quantarium_OpenLien_20250414_00018.TSV
- File 19: Quantarium_OpenLien_20250414_00019.TSV
- File 20: Quantarium_OpenLien_20250414_00020.TSV
- File 21: Quantarium_OpenLien_20250414_00021.TSV
- File 22: Quantarium_OpenLien_20250414_00022.TSV
- File 23: Quantarium_OpenLien_20250414_00023.TSV
- File 24: Quantarium_OpenLien_20250414_00024.TSV
- File 25: Quantarium_OpenLien_20250414_00025.TSV
- File 26: Quantarium_OpenLien_20250414_00026.TSV
- File 27: Quantarium_OpenLien_20250414_00027.TSV
- File 28: Quantarium_OpenLien_20250414_00028.TSV
- File 29: Quantarium_OpenLien_20250414_00029.TSV
- File 30: Quantarium_OpenLien_20250414_00030.TSV
- File 31: Quantarium_OpenLien_20250414_00031.TSV
- File 32: Quantarium_OpenLien_20250414_00032.TSV

Download Progress:
=================
ZIP Files Downloaded: __ / 31 remaining
TSV Files Extracted: __ / 32 total
Ready for Processing: __ / 32 total

Notes:
======
- Each file is approximately 6.1 GB uncompressed
- Total dataset: ~160 million property records
- QVM coverage expected: ~38.4% (61+ million valued properties)
"@

Set-Content -Path $trackingFile -Value $trackingContent
Write-Host "✅ Created tracking file: $trackingFile" -ForegroundColor Green

# Create README file with instructions
$readmeFile = Join-Path $mainPath "README.txt"
$readmeContent = @"
DataNest Massive Loading Project
===============================
Created: $(Get-Date)

FOLDER STRUCTURE:
├── downloaded-zip\     # ZIP files from FTP (32 files, ~32GB)
├── extracted-tsv\      # Uncompressed TSV files (32 files, ~195GB)  
├── completed\          # Successfully processed files
├── logs\              # Processing logs and tracking
└── scripts\           # Loading scripts and utilities

TOMORROW'S PROCESS:
1. Verify all 32 TSV files are in extracted-tsv\ folder
2. Run infrastructure scaling (8:00 AM)
3. Execute parallel loading (10:00 AM - 11:00 PM)
4. Post-load optimization (11:00 PM - 1:00 AM)

EXPECTED RESULTS:
- 160+ million property records loaded
- 61+ million properties with QVM valuations
- Database ready for API development
- All temporary infrastructure automatically scaled back

COST: ~$500-1000 for temporary scaling (auto scale-down included)
TIME: 12-24 hours total execution

Good luck with the massive scale loading! 🚀
"@

Set-Content -Path $readmeFile -Value $readmeContent
Write-Host "✅ Created README: $readmeFile" -ForegroundColor Green

Write-Host "`n🎯 SETUP COMPLETE!" -ForegroundColor Green
Write-Host "✅ File structure created" -ForegroundColor Green
Write-Host "✅ Tracking files generated" -ForegroundColor Green
Write-Host "✅ Disk space verified" -ForegroundColor Green

Write-Host "`n📋 TONIGHT'S CHECKLIST:" -ForegroundColor Cyan
Write-Host "1. Download 31 remaining ZIP files from FTP → C:\DataNest-TSV-Files\downloaded-zip\" -ForegroundColor White
Write-Host "2. Extract all ZIP files → C:\DataNest-TSV-Files\extracted-tsv\" -ForegroundColor White
Write-Host "3. Verify all 32 TSV files are ~6.1GB each" -ForegroundColor White
Write-Host "4. Update file_processing_tracker.txt with progress" -ForegroundColor White
Write-Host "5. Get good sleep for tomorrow's marathon! 😴" -ForegroundColor White

Write-Host "`n🚀 Tomorrow we load 160+ million records and make DataNest history!" -ForegroundColor Green 