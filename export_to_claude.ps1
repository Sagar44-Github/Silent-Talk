# SilentTalk - Smart Project Export for Claude
# Exports ONLY actual source code, not sign data/animation files

$projectRoot = "d:\Semester - 4\Full Stack Development\SilentTalk - The Project"
$outputFile  = Join-Path $projectRoot "SILENTTALK_FULL_EXPORT.txt"

$filesToExport = @()

# --- 1. Root-level documentation ---
$rootDocs = @('PROJECT_DOCUMENTATION.md', 'guide_text.txt', 'IEE-Abstract')
foreach ($f in $rootDocs) {
    $path = Join-Path $projectRoot $f
    if (Test-Path $path) { $filesToExport += Get-Item $path }
}

# --- 2. Django app (silenttalk/) ---
$djangoPath = Join-Path $projectRoot "silenttalk"
if (Test-Path $djangoPath) {
    $djangoFiles = Get-ChildItem -Path $djangoPath -Recurse -File | Where-Object {
        $ext = $_.Extension.ToLower()
        $validExt = @('.py', '.html', '.css', '.js', '.json', '.yml', '.yaml')
        if ($validExt -notcontains $ext) { return $false }
        if ($_.FullName -match '__pycache__') { return $false }
        if ($_.FullName -match 'migrations\\0') { return $false }
        if ($_.FullName -match 'hamnosysData') { return $false }
        if ($_.FullName -match 'SignFiles') { return $false }
        if ($_.Name -eq 'sigmlFiles.json') { return $false }
        if ($_.Name -eq 'allcsa.js') { return $false }  # CWASA engine, huge minified
        if ($_.Length -gt 102400) { return $false }
        return $true
    }
    $filesToExport += $djangoFiles
}

# Include words.txt (ISL vocabulary list)
$wordsTxt = Join-Path $projectRoot "silenttalk\recognition\static\recognition\words.txt"
if (Test-Path $wordsTxt) { $filesToExport += Get-Item $wordsTxt }

# --- 3. ActionDetectionforSignLanguage - key source only ---
$actionDir = Join-Path $projectRoot "ActionDetectionforSignLanguage"
if (Test-Path $actionDir) {
    $actionPy = Get-ChildItem -Path $actionDir -File -Filter "*.py" | Where-Object { $_.FullName -notmatch 'venv' }
    $filesToExport += $actionPy
}

# --- 4. AudioToSignLanguageConverter - core source only ---
$audioDir = Join-Path $projectRoot "AudioToSignLanguageConverter"
if (Test-Path $audioDir) {
    $audioCore = Get-ChildItem -Path $audioDir -File | Where-Object {
        $ext = $_.Extension.ToLower()
        $validExt = @('.py', '.html', '.css', '.js', '.json', '.md')
        ($validExt -contains $ext) -and ($_.Length -lt 102400)
    }
    $filesToExport += $audioCore
}

# --- 5. Sign-Language-to-Text-and-Speech - all .py files ---
$signDir = Join-Path $projectRoot "Sign-Language-to-Text-and-Speech"
if (Test-Path $signDir) {
    $signFiles = Get-ChildItem -Path $signDir -File | Where-Object {
        $ext = $_.Extension.ToLower()
        $validExt = @('.py', '.md', '.txt')
        ($validExt -contains $ext) -and ($_.Length -lt 102400) -and ($_.FullName -notmatch 'venv')
    }
    $filesToExport += $signFiles
}

# --- 6. stitch_sign_recognition - ONE sample HTML per design ---
$stitchDir = Join-Path $projectRoot "stitch_sign_recognition"
if (Test-Path $stitchDir) {
    $stitchDirs = Get-ChildItem -Path $stitchDir -Directory
    foreach ($d in $stitchDirs) {
        $indexHtml = Join-Path $d.FullName "index.html"
        if (Test-Path $indexHtml) {
            $item = Get-Item $indexHtml
            if ($item.Length -lt 51200) { $filesToExport += $item }
        }
    }
}

# Remove duplicates
$filesToExport = $filesToExport | Sort-Object FullName -Unique

# ============================================================
# BUILD OUTPUT
# ============================================================

$line = "=" * 66
$dash = "-" * 60

$sb = New-Object System.Text.StringBuilder
[void]$sb.AppendLine($line)
[void]$sb.AppendLine("  SILENTTALK - COMPLETE PROJECT EXPORT FOR CLAUDE")
[void]$sb.AppendLine("  Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')")
[void]$sb.AppendLine("  Total source files: $($filesToExport.Count)")
[void]$sb.AppendLine($line)
[void]$sb.AppendLine("")
[void]$sb.AppendLine("PROJECT TITLE:")
[void]$sb.AppendLine("Silent Talk: An Artificial Intelligence Based Indian Sign Language")
[void]$sb.AppendLine("Recognition and Real-Time Bidirectional Speech Conversion Web Platform")
[void]$sb.AppendLine("")
[void]$sb.AppendLine("AUTHOR: Sagar R | 4th Sem CSE | DSATM | FSD PBL 23CSE46")
[void]$sb.AppendLine("")
[void]$sb.AppendLine("TECH STACK:")
[void]$sb.AppendLine("- Backend: Django 5.x, Python 3.10+, PostgreSQL")
[void]$sb.AppendLine("- AI/ML: MediaPipe, TensorFlow (LSTM), Scikit-learn (Random Forest)")
[void]$sb.AppendLine("- NLP: Stanford Parser, NLTK")
[void]$sb.AppendLine("- Frontend: HTML5, CSS3, TailwindCSS, JavaScript, jQuery (AJAX)")
[void]$sb.AppendLine("- Avatar: CWASA/JAS (Signing Gesture Markup Language)")
[void]$sb.AppendLine("- Deployment: AWS Elastic Beanstalk")
[void]$sb.AppendLine("")
[void]$sb.AppendLine("THREE MODES:")
[void]$sb.AppendLine("Mode 1: Letter-level ASL recognition (MediaPipe + Random Forest, 38 classes)")
[void]$sb.AppendLine("Mode 2: Word-level gesture recognition (LSTM on 1662 holistic keypoints)")
[void]$sb.AppendLine("Mode 3: Speech-to-ISL reverse channel (Stanford Parser + CWASA 3D avatar)")
[void]$sb.AppendLine("")
[void]$sb.AppendLine("BINARY FILES NOT INCLUDED (these are trained ML models, not source code):")
[void]$sb.AppendLine("- action.h5 (6.9 MB) - LSTM model for word gesture recognition")
[void]$sb.AppendLine("- model.p (3.4 MB) - Random Forest model for letter recognition")
[void]$sb.AppendLine("")
[void]$sb.AppendLine("DATA FILES NOT INCLUDED (too large, repetitive sign animation data):")
[void]$sb.AppendLine("- hamnosysData/ - ~80 HamNoSys sign notation files (52-88 KB each)")
[void]$sb.AppendLine("- SignFiles/ - 848 SIGML sign animation XML files")
[void]$sb.AppendLine("- allcsa.js - CWASA avatar rendering engine (minified, 379 KB)")
[void]$sb.AppendLine("- sigmlFiles.json - mapping of 850+ words to SIGML files")
[void]$sb.AppendLine("")
[void]$sb.AppendLine($line)
[void]$sb.AppendLine("                    FILE CONTENTS BEGIN")
[void]$sb.AppendLine($line)

# File index
[void]$sb.AppendLine("")
[void]$sb.AppendLine("FILE INDEX")
[void]$sb.AppendLine($dash)
$counter = 1
foreach ($file in $filesToExport) {
    $relPath = $file.FullName.Replace($projectRoot + '\', '')
    $sizeKB  = [math]::Round($file.Length / 1KB, 1)
    [void]$sb.AppendLine("  $counter. $relPath  ($sizeKB KB)")
    $counter++
}
[void]$sb.AppendLine($dash)
[void]$sb.AppendLine("")

# File contents
$counter = 1
foreach ($file in $filesToExport) {
    $relPath = $file.FullName.Replace($projectRoot + '\', '')
    $sizeKB  = [math]::Round($file.Length / 1KB, 1)

    [void]$sb.AppendLine("")
    [void]$sb.AppendLine($line)
    [void]$sb.AppendLine("FILE $counter / $($filesToExport.Count): $relPath")
    [void]$sb.AppendLine("Size: $sizeKB KB  |  Modified: $($file.LastWriteTime.ToString('yyyy-MM-dd HH:mm'))")
    [void]$sb.AppendLine($line)

    try {
        $content = Get-Content -Path $file.FullName -Raw -Encoding UTF8 -ErrorAction Stop
        if ($content) {
            [void]$sb.AppendLine($content)
        } else {
            [void]$sb.AppendLine("[EMPTY FILE]")
        }
    } catch {
        [void]$sb.AppendLine("[ERROR: Could not read this file]")
    }
    $counter++
}

# Footer
[void]$sb.AppendLine("")
[void]$sb.AppendLine($line)
[void]$sb.AppendLine("                    END OF EXPORT")
[void]$sb.AppendLine("              Total files exported: $($filesToExport.Count)")
[void]$sb.AppendLine($line)

$sb.ToString() | Out-File -FilePath $outputFile -Encoding UTF8

$totalSizeKB = [math]::Round((Get-Item $outputFile).Length / 1KB, 1)
$totalSizeMB = [math]::Round((Get-Item $outputFile).Length / 1MB, 2)
Write-Host ""
Write-Host "Export complete!" -ForegroundColor Green
Write-Host "   Output: $outputFile"
Write-Host "   Files:  $($filesToExport.Count)"
Write-Host "   Size:   $totalSizeKB KB ($totalSizeMB MB)"
Write-Host ""
Write-Host "HOW TO USE:" -ForegroundColor Cyan
Write-Host "   1. Go to claude.ai"
Write-Host "   2. Click the paperclip icon to attach a file"
Write-Host "   3. Upload SILENTTALK_FULL_EXPORT.txt"
Write-Host "   4. Ask Claude your question about the project"
Write-Host ""
