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
# --------
# Optional
# --------
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
#
# ...or run res.sh without an argument to toggle between tv and office.
#

tvMode () {
	xrandr --output DVI-I-0 --mode 1280x720_60.00 --rotate normal
	xrandr --output HDMI-0 --off
	xrandr --output DVI-D-0 --off
	xrandr --output DP-1 --off
}

officeMode () {
	xrandr --output DVI-I-0 --mode 1920x1080 --rotate inverted --primary
	xrandr --output HDMI-0 --mode 1680x1050 --rotate left --right-of DVI-I-0
	xrandr --output DVI-D-0 --mode 1920x1080 --rotate inverted --left-of DVI-I-0
	xrandr --output DP-1 --mode 1680x1050 --rotate left --right-of HDMI-0
}

# Check argument(s) and change screen resolution(s) accordingly
if [[ $1 ]]; then
	if [ $1 == "--tv" ]; then
		tvMode
	fi

	if [ $1 == "--office" ]; then
		officeMode
	fi

	if [ $1 != "--tv" ] && [ $1 != "--office" ]; then
		echo "Invalid argument."
		exit
	fi
fi

# If there was no argument...
if [[ ! $1 ]]; then

	# Count the number of lines that have asterisk's in xrandr output
	monitorCount="$(xrandr | grep -i "*" | wc -l)"

	# Toggle output mode to opposite of current mode based on monitor count
	if [ "$monitorCount" == "1" ]; then
		officeMode
	fi
	
	if [ "$monitorCount" != "1" ]; then
		tvMode
	fi
fi

# Scratch
#argumentCount=$#
#echo $monitorCount