
terminateWindow := %1%

if WinExist(%terminateWindow%) {
	WinActivate
	if WinActive(%terminateWindow%) {
		Send "^{c}"
		Sleep 1000
		Send "^{c}"
		Sleep 10000
		Send "Y"
		Send "{Enter}"
		ExitApp 1
	}
} else {
	ExitApp 0
}