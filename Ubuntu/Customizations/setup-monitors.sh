#!/bin/bash
#
# Yes, this is a horrible solution, it just needs to work and I can understand why xorg.conf hates me later.
sleep 30
xrandr --output HDMI-0 --mode "1920x1080" --left-of DVI-D-0
sleep 5
xrandr --newmode "1680x1050_60.00"  146.25  1680 1784 1960 2240  1050 1053 1059 1089 -hsync +vsync
xrandr --addmode DP-1 "1680x1050_60.00"
xrandr --output DP-1 --mode "1680x1050_60.00" --rotate left --right-of DVI-D-0
sleep 5
xrandr --newmode "1680x1050_60.00_2"  146.25  1680 1784 1960 2240  1050 1053 1059 1089 -hsync +vsync
xrandr --addmode DVI-I-1 "1680x1050_60.00_2"
xrandr --output DVI-I-1 --mode "1680x1050_60.00_2" --rotate left --right-of DP-1
sleep 5
xrandr --noprimary
xrandr --output DVI-D-0 --primary
sleep 5
python -u /usr/share/screenlets/screenlets-pack-all/FolderView/FolderViewScreenlet.py > /dev/null