#!/bin/bash

sudo grep -RInaE \
'queryWindowInfo|setMaximi|maximi.*window|org\.kde\.KWin' \
chroot/usr/share \
chroot/usr/lib \
2>/dev/null | head -100
