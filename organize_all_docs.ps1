# Complete Documentation Organization Script
# Moves ALL documentation files to the docs/ folder

Write-Host "Organizing ALL PCA Agent Documentation..." -ForegroundColor Cyan
Write-Host ""

$projectRoot = Get-Location
$movedCount = 0
$skippedCount = 0

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
            Write-Host "  [OK] $FileName" -ForegroundColor Green
            return $true
        } catch {
            Write-Host "  [ERROR] $FileName : $_" -ForegroundColor Red
            return $false
        }
    } else {
        return $false
    }
}

# Architecture Documentation
Write-Host "Architecture Documentation:" -ForegroundColor Cyan
if (Move-DocFile "DOMAIN_EXPERTISE.md" "docs\architecture\") { $movedCount++ }
$skippedCount++
Write-Host ""

# User Guides
Write-Host "User Guides:" -ForegroundColor Cyan
if (Move-DocFile "GETTING_STARTED.md" "docs\user-guides\") { $movedCount++ }
if (Move-DocFile "QUICK_START.md" "docs\user-guides\") { $movedCount++ }
if (Move-DocFile "CSV_GUIDE.md" "docs\user-guides\") { $movedCount++ }
if (Move-DocFile "FUNNEL_DATASET_GUIDE.md" "docs\user-guides\") { $movedCount++ }
if (Move-DocFile "PLATFORM_DATASETS_GUIDE.md" "docs\user-guides\") { $movedCount++ }
if (Move-DocFile "BULK_ANALYSIS_GUIDE.md" "docs\user-guides\") { $movedCount++ }
if (Move-DocFile "MEDIA_TERMINOLOGY_GUIDE.md" "docs\user-guides\") { $movedCount++ }
if (Move-DocFile "METRIC_CALCULATION_GUIDE.md" "docs\user-guides\") { $movedCount++ }
if (Move-DocFile "QUERY_ENGINE_GUIDE.md" "docs\user-guides\") { $movedCount++ }
if (Move-DocFile "QA_TRAINING_GUIDE.md" "docs\user-guides\") { $movedCount++ }
if (Move-DocFile "TRAINING_GUIDE.md" "docs\user-guides\") { $movedCount++ }
if (Move-DocFile "ENTERPRISE_GUIDE.md" "docs\user-guides\") { $movedCount++ }
Write-Host ""

# API Reference
Write-Host "API Reference:" -ForegroundColor Cyan
if (Move-DocFile "API_KEYS_SETUP.md" "docs\api-reference\") { $movedCount++ }
Write-Host ""

# Development Documentation
Write-Host "Development Documentation:" -ForegroundColor Cyan
if (Move-DocFile "BENCHMARK_TRAINING_STATUS.md" "docs\development\") { $movedCount++ }
if (Move-DocFile "TRAINING_COMPLETE_SUMMARY.md" "docs\development\") { $movedCount++ }
if (Move-DocFile "SCENARIO_QUESTION_MAPPING.md" "docs\development\") { $movedCount++ }
Write-Host ""

# Planning & Features
Write-Host "Planning & Features:" -ForegroundColor Cyan
if (Move-DocFile "PROJECT_SUMMARY.md" "docs\planning\") { $movedCount++ }
if (Move-DocFile "FEATURES.md" "docs\planning\") { $movedCount++ }
if (Move-DocFile "ADVANCED_DATA_FEATURES.md" "docs\planning\") { $movedCount++ }
if (Move-DocFile "ENTERPRISE_FEATURES_SUMMARY.md" "docs\planning\") { $movedCount++ }
if (Move-DocFile "LARGE_DATASETS_SUMMARY.md" "docs\planning\") { $movedCount++ }
Write-Host ""

# Keep in root (don't move)
Write-Host "Keeping in root:" -ForegroundColor Yellow
Write-Host "  [KEEP] README.md (main project README)" -ForegroundColor Yellow
Write-Host "  [KEEP] INDEX.md (will be moved to docs/)" -ForegroundColor Yellow
Write-Host ""

# Move INDEX.md to docs if it exists in root
if (Test-Path "INDEX.md") {
    if (Move-DocFile "INDEX.md" "docs\") { 
        $movedCount++
        Write-Host "  [OK] Moved INDEX.md to docs/" -ForegroundColor Green
    }
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "  Files moved: $movedCount" -ForegroundColor Green
Write-Host "  Files kept in root: 1 (README.md)" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "SUCCESS: Documentation organized!" -ForegroundColor Green
Write-Host ""
Write-Host "Documentation structure:" -ForegroundColor Cyan
Write-Host "  docs/" -ForegroundColor White
Write-Host "    - architecture/    (system design)" -ForegroundColor Gray
Write-Host "    - user-guides/     (user documentation)" -ForegroundColor Gray
Write-Host "    - api-reference/   (API docs)" -ForegroundColor Gray
Write-Host "    - development/     (dev docs)" -ForegroundColor Gray
Write-Host "    - planning/        (planning & features)" -ForegroundColor Gray
Write-Host ""
Write-Host "View: docs/README.md" -ForegroundColor Cyan
Write-Host ""
