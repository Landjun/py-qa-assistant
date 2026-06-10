# Python 学习答疑客服系统 - 停止脚本
$oldPids = (netstat -ano | Select-String "0.0.0.0:8000.*LISTENING").Line `
           -replace '.*LISTENING\s+', '' -replace '\s.*', '' | Select-Object -Unique
foreach ($p in $oldPids) {
    if ($p -match '^\d+$') {
        Write-Host "停止 PID $p" -ForegroundColor Yellow
        Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
    }
}
Write-Host "服务已停止" -ForegroundColor Green
