#!/bin/bash

wal -i "$WALLPAPERS" -t

# Refresh bspwm's colorscheme
source "/home/emilien/.cache/wal/colors.sh"
bspc config normal_border_color $color0
bspc config focused_border_color $color1
bspc config active_border_color $color1
bspc config presel_feedback_color $color1
