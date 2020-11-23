#!/bin/bash
# apt-get install -y python3-pip
# curl -sSL https://get.docker.com | sh
# pip3 -v install docker-compose
# pip3 install -f /root/install/requirements.txt
if [ -f .env ]
then
  set -o allexport; source .env; set +o allexport
fi
mkdir -p $ROOT_DIR
mkdir -p "${ROOT_DIR}/static"
mkdir -p "${ROOT_DIR}/snapshot"
mkdir -p /nginx/conf
cp nginx/app_nginx.conf /nginx/conf/app_nginx.conf
cp nginx/uwsgi_params /nginx/uwsgi_params
# cp /root/concierge/stream_video.service /lib/systemd/system/
# systemctl enable stream_video.service
# systemctl start stream_video.service
RAMDISK="tmpfs  ${ROOT_DIR}/snapshot  tmpfs  rw,size=512M  0   0"
grep -qF "tmpfs" /etc/fstab || echo "${RAMDISK}" >> /etc/fstab
