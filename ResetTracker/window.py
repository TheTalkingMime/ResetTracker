import sys

# import all of the platform spesific things
if sys.platform.startswith("win32"):
	import win32gui
elif sys.platform.startswith("linux"):
	import sys
	import os
	import subprocess
	import re
elif sys.platform.startswith("darwin"):
	from AppKit import NSWorkspace

def get_window_name():
	if sys.platform.startswith("win32"):
		return win32gui.GetWindowText(win32gui.GetForegroundWindow())
	elif sys.platform.startswith("linux"):
		root = subprocess.Popen(['xprop', '-root', '_NET_ACTIVE_WINDOW'], stdout=subprocess.PIPE)
		stdout, stderr = root.communicate()
		m = re.search(b'^_NET_ACTIVE_WINDOW.* ([\w]+)$', stdout)
		if m != None:
			window_id = m.group(1)
			window = subprocess.Popen(['xprop', '-id', window_id, 'WM_NAME'], stdout=subprocess.PIPE)
			stdout, stderr = window.communicate()
		else:
			return ""
		match = re.match(b"WM_NAME\(\w+\) = (?P<name>.+)$", stdout)
		if match != None:
			return match.group("name").strip(b'"').decode("utf-8")
		return ""
	elif sys.platform.startswith("darwin"):
		return NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationName']