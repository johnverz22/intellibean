#!/bin/bash
# Launch HMI from SSH — finds the active Wayland/X display automatically
export DISPLAY=:0
export WAYLAND_DISPLAY=wayland-1
export XDG_RUNTIME_DIR=/run/user/1000
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus

pkill -9 -f hardware_test.py 2>/dev/null
sleep 1

nohup python3 /home/beans/bean_sorter/hardware_test.py \
    > /tmp/hmi.log 2>&1 &

echo "HMI PID: $!"
sleep 3
tail -20 /tmp/hmi.log
