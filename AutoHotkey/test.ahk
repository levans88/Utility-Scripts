#noenv
#singleinstance, force
DetectHiddenWindows, On
;onexit, Exit

Gui, +lastfound
hwnd_gui1 := winexist()
Run rundll32.exe shell32.dll`,Control_RunDLL "mmsys.cpl",, Hide, PID
winwait, ahk_pid %pid%
hwnd := WinExist("ahk_pid " . PID)
Set_Parent(hwnd_gui1, hwnd)
Return
 
;Exit:
	Process, Close, %pid%
;ExitApp


Set_Parent(Parent_hwmd, Child_hwnd)
{
   Return DllCall("SetParent", "uint", Child_hwnd, "uint", Parent_hwmd)
}