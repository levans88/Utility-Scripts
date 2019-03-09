#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
#Warn  ; Recommended for catching common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.
;Re-map Media Keys, coded in the order that they appear from left to right

;Misc
;space:: Send {space}
;space & Tab:: send {backspace}
;Tab & space:: send {Delete}

;CapsLock::
;If ScrollLockState = U
;If GetKeyState("XButton1", "P" = Off
;   send {enter}
;else send {LButton}
;Return

;Browser_Home
Browser_Home:: Run c:\windows\explorer.exe c:\windows\system32\snippingtool.exe

;Launch_Mail
;Launch_Mail:: send administrator{Tab}

;Launch_App1
;Launch_App1:: send _____

;c:\windows\system32\SnippingTool.exe

;Launch_App2
;Launch_App2:: send _____

;SKIP MAGNIFIER 1, not mappable

;SKIP MAGNIFIER 2, not mappable

;Media_Prev

;Media_Play_Pause

;Media_Next

;Volume_Mute

;Launch_Media

XButton1:: ^q

;(WASD)letters with direction and direction with selection keys
LShift & w::
      ;If GetKeyState("XButton1","P")
      ;   send +{up}
	  ;else 
      send {up}
Return

LShift & a::
      ;If GetKeyState("XButton1","P")
      ;   send +{left}
      ;else 
      send {left}
Return

LShift & s::
      ;If GetKeyState("XButton1","P")
      ;   send +{down}
	  ;else 
      send {down}
Return

LShift & d::
      ;If GetKeyState("XButton1","P")
      ;   send +{right}
	  ;else 
      send {right}
Return