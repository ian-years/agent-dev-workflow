# Agent Dev Workflow - Install Script (Windows PowerShell)
# Usage: powershell -ExecutionPolicy Bypass -File install.ps1

$skillsDest = "$env:USERPROFILE\.codex\skills"
$agentsDest = "$env:USERPROFILE\.codex\agents"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Installing Agent Dev Workflow..." -ForegroundColor Cyan

# Create directories
New-Item -ItemType Directory -Force -Path $skillsDest | Out-Null
New-Item -ItemType Directory -Force -Path $agentsDest | Out-Null

# Install skills (including references/)
$skills = @("feature-dev", "bugfix", "code-review", "design", "quick-code")
foreach ($skill in $skills) {
    $srcDir = Join-Path $scriptDir "skills\$skill"
    $dstDir = Join-Path $skillsDest $skill
    New-Item -ItemType Directory -Force -Path $dstDir | Out-Null
    Copy-Item "$srcDir\SKILL.md" "$dstDir\SKILL.md" -Force
    # Copy references if they exist
    $refsDir = Join-Path $srcDir "references"
    if (Test-Path $refsDir) {
        $dstRefs = Join-Path $dstDir "references"
        New-Item -ItemType Directory -Force -Path $dstRefs | Out-Null
        Copy-Item "$refsDir\*" "$dstRefs\" -Recurse -Force
    }
    Write-Host "  Skill: $skill installed" -ForegroundColor Green
}

# Install agents
$agents = @("architect", "coder", "debugger", "reviewer")
foreach ($agent in $agents) {
    $srcFile = Join-Path $scriptDir "agents\$agent.md"
    $agentContent = Get-Content -Raw -Encoding UTF8 $srcFile
    if ($agentContent -match "your-(strong|efficient)-model") {
        throw "Agent '$agent' still contains a placeholder model. Replace your-strong-model or your-efficient-model before installing."
    }
    Copy-Item $srcFile "$agentsDest\$agent.md" -Force
    Write-Host "  Agent: $agent installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "Installation complete!" -ForegroundColor Cyan
Write-Host "Skills installed to: $skillsDest" -ForegroundColor Gray
Write-Host "Agents installed to: $agentsDest" -ForegroundColor Gray
Write-Host ""
Write-Host "Restart Codex, then try saying:" -ForegroundColor Yellow
Write-Host "  - 'I want to build a new feature: [describe]'" -ForegroundColor White
Write-Host "  - 'Fix a bug: [describe]'" -ForegroundColor White
Write-Host "  - 'Review my recent changes'" -ForegroundColor White
Write-Host "  - 'Help me design a caching solution'" -ForegroundColor White
Write-Host "  - 'Add a phone field to the User model'" -ForegroundColor White
