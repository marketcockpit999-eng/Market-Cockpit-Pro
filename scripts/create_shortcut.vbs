Set WshShell = CreateObject("WScript.Shell")
Set shortcut = WshShell.CreateShortcut(WshShell.SpecialFolders("Desktop") & "\Market Cockpit Pro.lnk")
shortcut.TargetPath = "C:\Users\81802\Desktop\Market Cockpit Pro.bat"
shortcut.WorkingDirectory = "C:\Users\81802\.gemini\antigravity\scratch\market_monitor"
shortcut.IconLocation = "C:\Users\81802\.gemini\antigravity\scratch\market_monitor\icon.ico"
shortcut.Description = "Market Cockpit Pro - Financial Dashboard"
shortcut.Save
