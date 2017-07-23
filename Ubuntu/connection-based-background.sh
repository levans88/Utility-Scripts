#!/bin/bash

while true ; do
	# Check for connections
	tun="$(ifconfig | grep "tun0")"
	ctun="$(ifconfig | grep "cscotun0")"
	background="$(dconf read /org/mate/desktop/background/picture-filename)"

	# Set background for connection tun
	if [[ $tun && ! $ctun && $background != "'/home/user/Pictures/red.png'" ]]; then
		dconf write /org/mate/desktop/background/picture-filename "'/home/user/Pictures/red.png'"
	fi

	# Set background for connection ctun
	if [[ $ctun && $background != "'/home/user/Pictures/orange.png'" ]]; then
		dconf write /org/mate/desktop/background/picture-filename "'/home/user/Pictures/orange.png'"

	fi

	# Restore background
	if [[ ! $tun && ! $ctun && $background != "'/home/user/Pictures/black.png'" ]]; then
		dconf write /org/mate/desktop/background/picture-filename "'/home/user/Pictures/black.png'"
	fi

	sleep 5
done