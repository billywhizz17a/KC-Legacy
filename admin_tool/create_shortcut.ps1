$ws = New-Object -ComObject WScript.Shell
$desktop = [Environment]::GetFolderPath("Desktop")
$sc = $ws.CreateShortcut("$desktop\KC Legacy Admin.lnk")
$sc.TargetPath = "pythonw"
$sc.Arguments = "admin_tool\server.py"
$sc.WorkingDirectory = "e:\CascadeProjects\kc_legacy_valeting"
$sc.IconLocation = "$env:LOCALAPPDATA\KCLegacyAdmin\icon.ico"
$sc.Description = "KC Legacy Admin - Package & Pricing Manager"
$sc.Save()
Write-Host "Shortcut created at: $desktop\KC Legacy Admin.lnk"
