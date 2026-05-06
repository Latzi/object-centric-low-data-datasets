$ErrorActionPreference = "Stop"

# Repo paths
$repoRoot = Split-Path -Parent $PSScriptRoot
$trafficRoot = Join-Path $repoRoot "traffic_signs"
$outFile = Join-Path $trafficRoot "metadata\traffic_signs_manifest.csv"

function To-RelativeTrafficPath([string]$fullPath) {
    $rel = $fullPath.Substring($trafficRoot.Length).TrimStart('\','/')
    return $rel -replace '\\','/'
}

$splitConfigs = @(
    @{
        split = "train"
        imageDir = Join-Path $trafficRoot "Train_Data\images\train"
        labelDir = Join-Path $trafficRoot "Train_Data\labels\train"
    },
    @{
        split = "val"
        imageDir = Join-Path $trafficRoot "Train_Data\images\val"
        labelDir = Join-Path $trafficRoot "Train_Data\labels\val"
    },
    @{
        split = "test"
        imageDir = Join-Path $trafficRoot "Train_Data\test\images"
        labelDir = Join-Path $trafficRoot "Train_Data\test\labels"
    }
)

$rows = @()

foreach ($cfg in $splitConfigs) {
    if (-not (Test-Path $cfg.imageDir)) {
        Write-Host "Skipping missing image folder: $($cfg.imageDir)"
        continue
    }

    $images = Get-ChildItem -Path $cfg.imageDir -File | Where-Object {
        $_.Extension.ToLower() -in @(".jpg", ".jpeg", ".png")
    } | Sort-Object Name

    foreach ($img in $images) {
        $sampleId = [System.IO.Path]::GetFileNameWithoutExtension($img.Name)
        $labelPath = Join-Path $cfg.labelDir ($sampleId + ".txt")

        $annotationRel = ""
        $numBoxes = 0
        $notes = ""

        if (Test-Path $labelPath) {
            $annotationRel = To-RelativeTrafficPath $labelPath
            $numBoxes = (Get-Content $labelPath | Where-Object { $_.Trim() -ne "" }).Count
        }
        else {
            $notes = "Missing label file"
        }

        $rows += [PSCustomObject]@{
            sample_id         = $sampleId
            image_relpath     = To-RelativeTrafficPath $img.FullName
            annotation_relpath= $annotationRel
            mask_relpath      = ""
            split             = $cfg.split
            class_id          = 0
            class_name        = "TrafficSigns"
            num_boxes         = $numBoxes
            released_width    = 256
            released_height   = 256
            annotation_format = "YOLO"
            notes             = $notes
        }
    }
}

$rows | Export-Csv -Path $outFile -NoTypeInformation -Encoding UTF8

Write-Host ""
Write-Host "Manifest written to:"
Write-Host $outFile
Write-Host ""
Write-Host "Total rows:" $rows.Count