#InstallKeybdHook
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.

;-------------------------
;Toggle Display Resolution
;-------------------------

Alt & Tab::
WinGetPos ,,, resWidth,, Program Manager 
;msgbox %resWidth%

If (resWidth = 1920){
	EncodeInteger1( p_value, p_size, p_address, p_offset )
	{
		loop, %p_size%
		DllCall( "RtlFillMemory"
			, "uint", p_address+p_offset+A_Index-1
			, "uint", 1
			, "uchar", ( p_value >> ( 8*( A_Index-1 ) ) ) & 0xFF )
	}

	colorDepth = 32 ; bits (quality)
	screenWidth = 1280 ; pixels
	screenHeight = 720 ; pixels
	refreshRate = 59 ; Hz (frequency)
	
	; Don't change anything below!
	struct_devicemode_size = 156
	VarSetCapacity(device_mode, struct_devicemode_size, 0)
	EncodeInteger1(struct_devicemode_size, 2, &device_mode, 36)
	success := DllCall("EnumDisplaySettings", "uint", 0, "uint", -1, "uint", &device_mode)

	; DM_BITSPERPEL|DM_PELSWIDTH|DM_PELSHEIGHT|DM_DISPLAYFREQUENCY
	EncodeInteger1(0x00040000|0x00080000|0x00100000|0x00400000, 4, &device_mode, 40)
	EncodeInteger1(colorDepth, 4, &device_mode, 104)
	EncodeInteger1(screenWidth, 4, &device_mode, 108)
	EncodeInteger1(screenHeight, 4, &device_mode, 112)
	EncodeInteger1(refreshRate, 4, &device_mode, 120)

	DllCall("ChangeDisplaySettings", "uint", &device_mode, "uint", 0)
}

else{
	EncodeInteger2( p_value, p_size, p_address, p_offset )
	{
	loop, %p_size%
		DllCall( "RtlFillMemory"
			, "uint", p_address+p_offset+A_Index-1
			, "uint", 1
			, "uchar", ( p_value >> ( 8*( A_Index-1 ) ) ) & 0xFF )
	}

	colorDepth = 32 ; bits (quality)
	screenWidth = 1920 ; pixels
	screenHeight = 1080 ; pixels
	refreshRate = 60 ; Hz (frequency)
	
	; Don't change anything below!
	struct_devicemode_size = 156
	VarSetCapacity(device_mode, struct_devicemode_size, 0)
	EncodeInteger2(struct_devicemode_size, 2, &device_mode, 36)
	success := DllCall("EnumDisplaySettings", "uint", 0, "uint", -1, "uint", &device_mode)

	; DM_BITSPERPEL|DM_PELSWIDTH|DM_PELSHEIGHT|DM_DISPLAYFREQUENCY
	EncodeInteger2(0x00040000|0x00080000|0x00100000|0x00400000, 4, &device_mode, 40)
	EncodeInteger2(colorDepth, 4, &device_mode, 104)
	EncodeInteger2(screenWidth, 4, &device_mode, 108)
	EncodeInteger2(screenHeight, 4, &device_mode, 112)
	EncodeInteger2(refreshRate, 4, &device_mode, 120)

	DllCall("ChangeDisplaySettings", "uint", &device_mode, "uint", 0)
}
return

;---------------------------
;Toggle Default Audio Device
;---------------------------

Launch_Mail::
Run mmsys.cpl
WinWait,Sound
ControlSend,SysListView321,{Down}
ControlGet, isEnabled, Enabled,,&Set Default
if(!isEnabled)
{
	ControlSend,SysListView321,{Down 2}
}
ControlClick,&Set Default
ControlClick,OK
WinWaitClose
SoundPlay, *-1
return
