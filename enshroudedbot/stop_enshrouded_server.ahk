
if WinExist("enshrouded_server.exe") {
	WinActivate
	if WinActive("enshrouded_server.exe") {
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