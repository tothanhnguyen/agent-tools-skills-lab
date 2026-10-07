$ErrorActionPreference = 'Stop'
$taskRepo = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location -LiteralPath $taskRepo
docker info --format '{{.ServerVersion}}'
if ($LASTEXITCODE -ne 0) { throw 'Start Docker Desktop, wait until its engine is running, then retry.' }
docker inspect agent-lab-posix --format '{{.Name}}' 2>$null
if ($LASTEXITCODE -ne 0) {
    docker build -t agent-lab-runtime .
    if ($LASTEXITCODE -ne 0) { throw 'Docker image build failed.' }
    docker run -d --name agent-lab-posix --mount "type=bind,source=$taskRepo,target=/lab" --mount 'type=volume,source=agent-lab-python,target=/opt/lab-venv' -p 127.0.0.1:8513:8513 -p 127.0.0.1:8514:8514 agent-lab-runtime
    if ($LASTEXITCODE -ne 0) { throw 'Container creation failed.' }
} else {
    docker start agent-lab-posix
    if ($LASTEXITCODE -ne 0) { throw 'Container start failed.' }
}
docker exec -w /lab agent-lab-posix uv sync --all-packages --locked
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
foreach ($taskStage in @(@{Name='stage-03-bash'; Port=8513}, @{Name='stage-04-script-skill'; Port=8514})) {
    $taskHealthy = $false
    try {
        $taskResponse = Invoke-WebRequest -Uri "http://127.0.0.1:$($taskStage.Port)/_stcore/health" -UseBasicParsing -TimeoutSec 2
        $taskHealthy = $taskResponse.StatusCode -eq 200
    } catch { }
    if (-not $taskHealthy) {
        docker exec -d -w "/lab/$($taskStage.Name)" agent-lab-posix uv run --locked streamlit run runtime/gemini_app.py --server.address 0.0.0.0 --server.port $taskStage.Port --browser.gatherUsageStats false
        if ($LASTEXITCODE -ne 0) { throw "Could not start $($taskStage.Name)." }
    }
    Write-Host "$($taskStage.Name): http://127.0.0.1:$($taskStage.Port)"
}
