$desktop = [System.Environment]::GetFolderPath('Desktop')
$shortcutPath = Join-Path $desktop "AMS_PRO_5.0_QLCV.lnk"
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = "d:\App_Claude_Antigravity\QLCV_web\chay_app.bat"
$shortcut.WorkingDirectory = "d:\App_Claude_Antigravity\QLCV_web"
$shortcut.Description = "Mo ung dung Quan Ly Cong Viec AMS PRO 5.0"
$shortcut.Save()
Write-Host "Shortcut created at $shortcutPath"
