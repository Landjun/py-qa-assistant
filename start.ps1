# Python 学习答疑客服系统 - 启动脚本
# 用法：右键 -> "用 PowerShell 运行"  或  powershell -File start.ps1

$ROOT    = Split-Path -Parent $MyInvocation.MyCommand.Path
$BACKEND = Join-Path $ROOT "backend"
$UV      = "C:\Users\Administrator\AppData\Local\Programs\Python\Python312\Scripts\uv.exe"
$LOG_OUT = Join-Path $ROOT "uvicorn.log"
$LOG_ERR = Join-Path $ROOT "uvicorn_err.log"

# 1. 停掉旧进程
Write-Host "停止旧进程..." -ForegroundColor Yellow
$oldPids = (netstat -ano | Select-String "0.0.0.0:8000.*LISTENING").Line `
           -replace '.*LISTENING\s+', '' -replace '\s.*', '' | Select-Object -Unique
foreach ($p in $oldPids) {
    if ($p -match '^\d+$') { Stop-Process -Id $p -Force -ErrorAction SilentlyContinue }
}
Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1

# 2. 启动 uvicorn
Write-Host "启动后端服务..." -ForegroundColor Green
$proc = Start-Process -FilePath $UV `
    -ArgumentList "run","uvicorn","app.main:app","--host","0.0.0.0","--port","8000" `
    -WorkingDirectory $BACKEND `
    -RedirectStandardOutput $LOG_OUT `
    -RedirectStandardError  $LOG_ERR `
    -WindowStyle Hidden -PassThru

Write-Host "已启动 (PID=$($proc.Id))，等待就绪..." -ForegroundColor Green
Start-Sleep -Seconds 5

# 3. 验证
try {
    $resp = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "启动成功！" -ForegroundColor Green
    Write-Host ""
    Write-Host "  本机访问:  http://localhost:8000" -ForegroundColor Cyan
    Write-Host "  局域网:    http://$(((Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.PrefixOrigin -ne 'WellKnown'})[0].IPAddress)):8000" -ForegroundColor Cyan
    Write-Host "  公网访问:  http://43.160.227.153:8000" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "日志: $LOG_ERR" -ForegroundColor Gray
} catch {
    Write-Host "启动失败，查看日志: $LOG_ERR" -ForegroundColor Red
    Get-Content $LOG_ERR -Tail 20
}
