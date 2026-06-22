Set sh = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
root = "E:\Projects\Nazmul-Tweaks-Tool"
sh.CurrentDirectory = root
sh.Run "cmd /c set BUILD_NO_UI=1 && BUILD.bat", 1, True
release = root & "\release\Nazmul-Tweaks-Tool.exe"
If fso.FileExists(release) Then
    size = fso.GetFile(release).Size
    sizeMB = Round(size / 1048576, 1)
    sh.Popup "BUILD SUCCESS!" & vbCrLf & vbCrLf & _
             "EXE ready:" & vbCrLf & release & vbCrLf & _
             "Size: " & sizeMB & " MB" & vbCrLf & vbCrLf & _
             "Upload release\Nazmul-Tweaks-Tool.exe to GitHub Releases.", _
             8, "Nazmul Tweaks Tool"
    sh.Run "explorer " & Chr(34) & root & "\release" & Chr(34), 1, False
Else
    sh.Popup "Build failed. Open build.log for details:" & vbCrLf & root & "\build.log", 16, "Nazmul Tweaks Tool"
    sh.Run "notepad " & Chr(34) & root & "\build.log" & Chr(34), 1, False
End If