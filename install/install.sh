#!/bin/bash
# apt-get install -y python3-pip
# apt-get install -y libssl-dev libmysqlclient-dev
# apt install -y python3-dev 
# apt install -y build-essential
# apt-get install -y libffi-dev
# curl -sSL https://get.docker.com | sh
# pip3 -v install docker-compose
pip3 install -r /root/concierge/install/requirements.txt
if [ -f .env ]
then
  set -o allexport; source .env; set +o allexport
fi
mkdir -p $ROOT_DIR
mkdir -p "${ROOT_DIR}/static"
mkdir -p "${ROOT_DIR}/static/recordings"
mkdir -p "${ROOT_DIR}/snapshot"
mkdir -p /nginx/conf
cp nginx/app_nginx.conf /nginx/conf/app_nginx.conf
cp nginx/uwsgi_params /nginx/uwsgi_params
# cp /root/concierge/stream_video.service /lib/systemd/system/
# systemctl enable stream_video.service
# systemctl start stream_video.service
# RAMDISK="tmpfs  ${ROOT_DIR}/snapshot  tmpfs  rw,size=512M  0   0"
# grep -qF "tmpfs" /etc/fstab || echo "${RAMDISK}" >> /etc/fstab
timedatectl set-timezone ${TIMEZONE}
# echo "Install opencv, this will take some time"
# apt install libopencv-dev python3-opencv
# apt install ubuntu-desktop

docker-compose build
docker-compose run gui python3 manage.py migrate
docker-compose run gui python3 manage.py collectstatic
docker-compose run gui python3 manage.py loaddata initial_data.json
# docker-compose run gui python3 manage.py dumpdata --natural-primary --natural-foreign --indent 4 -e sessions -e admin -e contenttypes -e auth.Permission > initial_data.json
echo "Installation finished, reboot now the system"
