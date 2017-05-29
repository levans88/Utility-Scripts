#!/bin/bash

# Script to toggle custom display settings.

# ---------------
# Notes and Setup
# ---------------
#
# Place this custom script in "/usr/local/bin"
#
# https://superuser.com/questions/595828/where-to-store-bash-scripts-that-all-users-may-execute-on-debian
#
# The "official" place for local executables is "/usr/local/bin".
# This directory is usually in the $PATH of all users by default.
#
# Traditionally, programs that are NOT installed through a package manager (eg apt) are stored
# in the "/usr/local/bin" directory and those installed by the package manager in "/usr/bin".
#
# To make executable and run from launcher:
#	sudo chmod +x res.sh
#
#	gksudo gedit ~/.local/share/applications/restv.desktop
#	(also make resoffice.desktop)	
#
# Paste in restv.desktop:
#	[Desktop Entry]
#	Type=Application
#	Name=Res TV
#	Icon=/usr/share/app-install/icons/mate-preferences-desktop-display.svg
#	Exec=/usr/local/bin/res.sh --tv
#
# Paste in resoffice.desktop:
#	[Desktop Entry]
#	Type=Application
#	Name=Res Office
#	Icon=/usr/share/app-install/icons/mate-preferences-desktop-display.svg
#	Exec=/usr/local/bin/res.sh --office

# Check argument(s) and change screen resolution(s) accordingly
if [[ $1 ]]; then
	if [ $1 == "--tv" ]; then
		xrandr --output DVI-I-1 --mode 1368x768_60.00 --rotate normal
		xrandr --output DVI-D-1 --off
		xrandr --output HDMI-1 --off
	fi

	if [ $1 == "--office" ]; then
		xrandr --output DVI-I-1 --mode 1920x1080_60.00 --rotate inverted --primary
		xrandr --output DVI-D-1 --mode 1920x1080 --rotate inverted --left-of DVI-I-1
		xrandr --output HDMI-1 --mode 1680x1050 --rotate left --right-of DVI-I-1
	fi
else
	echo "no argument supplied"
	exit
fi

# Scratch
#argumentCount=$#