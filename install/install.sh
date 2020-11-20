#!/bin/bash
apt-get install python3-pip
curl -sSL https://get.docker.com | sh
pip3 -v install docker-compose
# apt-get install omxplayer
pip3 install -f /root/install/requirements.txt
# cp /root/concierge/stream_video.service /lib/systemd/system/
# systemctl enable stream_video.service
# systemctl start stream_video.service
