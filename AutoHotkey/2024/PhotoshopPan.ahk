#IfWinActive ahk_class Photoshop
~MButton::
    Send {Space Down}
    Send {LButton Down}
return

~MButton Up::
    Send {Space Up}
    Send {LButton Up}
return
#IfWinActive
