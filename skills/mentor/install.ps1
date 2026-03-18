param(
    [ValidateSet("codex", "claude", "both")]
    [string]$Target = "both",

    [ValidateSet("copy", "link")]
    [string]$Mode = "copy",

    [ValidateSet("personal", "project")]
    [string]$Scope = "personal",

    [string]$ProjectDir = ""
)

$ErrorActionPreference = "Stop"

$SkillName = "mentor"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SourceItems = @("SKILL.md", "README.md", "agents", "scripts", "references", "assets")

function Install-Copy {
    param([string]$Destination)

    if (Test-Path -LiteralPath $Destination) {
        Remove-Item -LiteralPath $Destination -Recurse -Force
    }

    New-Item -ItemType Directory -Path $Destination -Force | Out-Null

    foreach ($Item in $SourceItems) {
        $SourcePath = Join-Path $ScriptDir $Item
        if (Test-Path -LiteralPath $SourcePath) {
            Copy-Item -LiteralPath $SourcePath -Destination $Destination -Recurse -Force
        }
    }

    Get-ChildItem -LiteralPath $Destination -Recurse -Directory -Filter "__pycache__" |
        Remove-Item -Recurse -Force

    Get-ChildItem -LiteralPath $Destination -Recurse -File -Include "*.pyc" |
        Remove-Item -Force
}

function Install-Link {
    param([string]$Destination)

    if (Test-Path -LiteralPath $Destination) {
        Remove-Item -LiteralPath $Destination -Recurse -Force
    }

    $Parent = Split-Path -Parent $Destination
    New-Item -ItemType Directory -Path $Parent -Force | Out-Null
    New-Item -ItemType SymbolicLink -Path $Destination -Target $ScriptDir | Out-Null
}

function Install-Target {
    param(
        [string]$Label,
        [string]$Destination
    )

    switch ($Mode) {
        "copy" { Install-Copy -Destination $Destination }
        "link" { Install-Link -Destination $Destination }
    }

    Write-Host ("Installed {0,-6} -> {1}" -f $Label, $Destination)
}

if ($Scope -eq "project" -and [string]::IsNullOrWhiteSpace($ProjectDir)) {
    $ProjectDir = (Get-Location).Path
}

if (-not [string]::IsNullOrWhiteSpace($ProjectDir) -and -not (Test-Path -LiteralPath $ProjectDir -PathType Container)) {
    throw "Project directory does not exist: $ProjectDir"
}

$AgentsBase = if ($env:AGENTS_HOME) { $env:AGENTS_HOME } else { Join-Path $HOME ".agents" }
$CodexTarget = Join-Path (Join-Path $AgentsBase "skills") $SkillName

if ($Scope -eq "project") {
    $ClaudeTarget = Join-Path (Join-Path $ProjectDir ".claude/skills") $SkillName
}
else {
    $ClaudeTarget = Join-Path (Join-Path $HOME ".claude/skills") $SkillName
}

if ($Target -eq "codex" -or $Target -eq "both") {
    Install-Target -Label "Codex" -Destination $CodexTarget
}

if ($Target -eq "claude" -or $Target -eq "both") {
    Install-Target -Label "Claude" -Destination $ClaudeTarget
}

Write-Host ""
Write-Host "Next:"
Write-Host "  Codex : start a new session, then invoke with `$mentor"
Write-Host "  Claude: start a new session, then invoke with /mentor"
