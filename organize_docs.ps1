# Documentation Organization Script
# Moves documentation files to the new docs/ folder structure

Write-Host "Organizing PCA Agent Documentation..." -ForegroundColor Cyan
Write-Host ""

# Get current directory
$projectRoot = Get-Location

# Function to move file safely
function Move-DocFile {
    param(
        [string]$FileName,
        [string]$Destination
    )
    
    $sourcePath = Join-Path $projectRoot $FileName
    $destPath = Join-Path $projectRoot $Destination
    
    if (Test-Path $sourcePath) {
        try {
            Move-Item -Path $sourcePath -Destination $destPath -Force
            Write-Host "  [OK] Moved: $FileName to $Destination" -ForegroundColor Green
            return $true
        } catch {
            Write-Host "  [ERROR] Failed to move $FileName : $_" -ForegroundColor Red
            return $false
        }
    } else {
        Write-Host "  [SKIP] Not found: $FileName" -ForegroundColor Yellow
        return $false
    }
}

# Counter for moved files
$movedCount = 0
$totalFiles = 0

Write-Host "Moving Architecture Documentation..." -ForegroundColor Cyan
$totalFiles += 3
if (Move-DocFile "ARCHITECTURE.md" "docs\architecture\") { $movedCount++ }
if (Move-DocFile "PREDICTIVE_ANALYTICS_ARCHITECTURE.md" "docs\architecture\") { $movedCount++ }
if (Move-DocFile "ANALYSIS_FRAMEWORK.md" "docs\architecture\") { $movedCount++ }
Write-Host ""

Write-Host "Moving User Guides..." -ForegroundColor Cyan
$totalFiles += 3
if (Move-DocFile "PREDICTIVE_IMPLEMENTATION_GUIDE.md" "docs\user-guides\") { $movedCount++ }
if (Move-DocFile "PREDICTIVE_QUICKSTART.md" "docs\user-guides\") { $movedCount++ }
if (Move-DocFile "DASHBOARD_USER_GUIDE.md" "docs\user-guides\") { $movedCount++ }
Write-Host ""

Write-Host "Moving Development Documentation..." -ForegroundColor Cyan
$totalFiles += 2
if (Move-DocFile "TEST_RESULTS_SUMMARY.md" "docs\development\") { $movedCount++ }
if (Move-DocFile "DEPLOYMENT.md" "docs\development\") { $movedCount++ }
Write-Host ""

Write-Host "Moving Planning Documentation..." -ForegroundColor Cyan
$totalFiles += 2
if (Move-DocFile "PROJECT_STATUS.md" "docs\planning\") { $movedCount++ }
if (Move-DocFile "DOCUMENTATION_PLAN.md" "docs\planning\") { $movedCount++ }
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "  Total files processed: $totalFiles" -ForegroundColor White
Write-Host "  Successfully moved: $movedCount" -ForegroundColor Green
Write-Host "  Not found/errors: $($totalFiles - $movedCount)" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($movedCount -eq $totalFiles) {
    Write-Host "SUCCESS: All documentation files organized!" -ForegroundColor Green
} elseif ($movedCount -gt 0) {
    Write-Host "PARTIAL: Some files organized. Others may not exist yet." -ForegroundColor Yellow
} else {
    Write-Host "INFO: No files moved. They may already be organized." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "New documentation structure:" -ForegroundColor Cyan
Write-Host "  docs/" -ForegroundColor White
Write-Host "    - architecture/" -ForegroundColor Gray
Write-Host "    - user-guides/" -ForegroundColor Gray
Write-Host "    - api-reference/" -ForegroundColor Gray
Write-Host "    - development/" -ForegroundColor Gray
Write-Host "    - planning/" -ForegroundColor Gray
Write-Host ""

Write-Host "View documentation index in: docs/README.md" -ForegroundColor Cyan
Write-Host ""
