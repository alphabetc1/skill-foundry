param(
    [string]$Skill = "all",

    [ValidateSet("codex", "claude", "both")]
    [string]$Target = "both",

    [ValidateSet("copy", "link")]
    [string]$Mode = "copy",

    [ValidateSet("personal", "project")]
    [string]$Scope = "personal",

    [string]$ProjectDir = "",

    [switch]$List
)

$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SkillsDir = Join-Path $RootDir "skills"

function Get-SkillNames {
    if (-not (Test-Path -LiteralPath $SkillsDir -PathType Container)) {
        throw "Skills directory does not exist: $SkillsDir"
    }

    Get-ChildItem -LiteralPath $SkillsDir -Directory |
        Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName "install.ps1") -PathType Leaf } |
        Select-Object -ExpandProperty Name |
        Sort-Object
}

if ($List) {
    Get-SkillNames | ForEach-Object { Write-Host $_ }
    exit 0
}

$AvailableSkills = @(Get-SkillNames)
if ($AvailableSkills.Count -eq 0) {
    throw "No installable skills found under $SkillsDir"
}

if ($Skill -eq "all") {
    $SelectedSkills = $AvailableSkills
}
elseif ($AvailableSkills -contains $Skill) {
    $SelectedSkills = @($Skill)
}
else {
    throw "Unknown skill: $Skill"
}

foreach ($Name in $SelectedSkills) {
    $Installer = Join-Path (Join-Path $SkillsDir $Name) "install.ps1"
    Write-Host "Installing $Name"
    & $Installer -Target $Target -Mode $Mode -Scope $Scope -ProjectDir $ProjectDir
    Write-Host ""
}
