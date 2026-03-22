#!/bin/bash
# Disable RealVNC auth and restart it
mkdir -p /home/beans/.vnc
cat > /home/beans/.vnc/config.d/vncserver-x11 << 'EOF'
Authentication=VncAuth
Password=
EOF

# Try the simpler approach — set no-auth via vncpasswd blank or use NullAuth
sudo vncserver-x11 -stop 2>/dev/null
pkill -f vncserver-x11 2>/dev/null
pkill -f Xvnc 2>/dev/null
sleep 1

# Start with no authentication
vncserver-x11 -Authentication=None &
sleep 2
echo "VNC started"
