# CTA-KG pipeline (no data in git — generates local demo artefacts only)
# Usage:  .\run_all.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$steps = @(
    @{ Name = "Generate local synthetic demo + preprocess"; Script = "src/generate_synthetic_data.py" },
    @{ Name = "Data dictionary";                            Script = "src/preprocess.py" },
    @{ Name = "Build RDF graph";                            Script = "src/build_graph.py" },
    @{ Name = "SHACL validate";                             Script = "src/validate.py" },
    @{ Name = "OWL-RL reason";                              Script = "src/reason.py" },
    @{ Name = "SPARQL competency queries";                  Script = "src/query.py" },
    @{ Name = "RO-Crate package (local)";                   Script = "src/package.py" }
)

Write-Host "CTA-KG pipeline — generated files stay local (gitignored)" -ForegroundColor Cyan

foreach ($step in $steps) {
    Write-Host ""
    Write-Host ">> $($step.Name)" -ForegroundColor Yellow
    & py $step.Script
    if ($LASTEXITCODE -ne 0) {
        Write-Host "FAILED: $($step.Script)" -ForegroundColor Red
        exit $LASTEXITCODE
    }
    Write-Host "   OK" -ForegroundColor Green
}

Write-Host ""
Write-Host "Done. Do not commit data/ or rdf/." -ForegroundColor Green
