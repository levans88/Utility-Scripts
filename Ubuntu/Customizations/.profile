# ~/.profile: executed by the command interpreter for login shells.
# This file is not read by bash(1), if ~/.bash_profile or ~/.bash_login
# exists.
# see /usr/share/doc/bash/examples/startup-files for examples.
# the files are located in the bash-doc package.

# the default umask is set in /etc/profile; for setting the umask
# for ssh logins, install and configure the libpam-umask package.
#umask 022

# if running bash
if [ -n "$BASH_VERSION" ]; then
    # include .bashrc if it exists
    if [ -f "$HOME/.bashrc" ]; then
	. "$HOME/.bashrc"
    fi
fi

# set PATH so it includes user's private bin directories
# and other customizations to PATH
PATH="$HOME/bin:$HOME/.local/bin:/usr/local/bin/pycharm-2017.1.4/bin:$PATH"


# Nvidia Resolutions
#
# Since ignoring EDID and using custom xorg.conf, 1280x720 is not available automatically...
xrandr --newmode "1280x720_60.00"   74.50  1280 1344 1472 1664  720 723 728 748 -hsync +vsync
xrandr --addmode DVI-I-0 "1280x720_60.00"


# Nouveau Resolutions
#
#No longer needed, standard 1920x1080 works and is auto found for TV and LCD once using VGA 
#cables instead of VGA over CAT5...
#cvt 1920 1080
#xrandr --newmode "1920x1080_60.00"  173.00  1920 2048 2248 2576  1080 1083 1088 1120 -hsync +vsync
#xrandr --addmode DVI-I-1 "1920x1080_60.00"

#cvt 1366 768
#xrandr --newmode "1368x768_60.00"   85.25  1368 1440 1576 1784  768 771 781 798 -hsync +vsync
#xrandr --addmode DVI-I-1 "1368x768_60.00"

#cvt 1360 768
#xrandr --newmode "1360x768_60.00"   84.75  1360 1432 1568 1776  768 771 781 798 -hsync +vsync
#xrandr --addmode DVI-I-1 "1360x768_60.00"

#cvt 1280 720
#xrandr --newmode "1280x720_60.00"   74.50  1280 1344 1472 1664  720 723 728 748 -hsync +vsync
#xrandr --addmode DVI-I-1 "1280x720_60.00"


# Other
#
# fix mouse acceleration / mouse too fast
xset m 0 0