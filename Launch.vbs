Set sh = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
root = "E:\Projects\Nazmul-Tweaks-Tool"
bat = root & "\Launch.bat"
If Not fso.FileExists(bat) Then
    MsgBox "Launch.bat not found at:" & vbCrLf & bat, 16, "Nazmul Tweaks Tool"
    WScript.Quit 1
End If
sh.CurrentDirectory = root
code = sh.Run("cmd /c """ & bat & """", 0, True)
If code <> 0 Then
    MsgBox "Failed to launch (exit " & code & ")." & vbCrLf & "Try running Launch.bat manually.", 16, "Nazmul Tweaks Tool"
End If