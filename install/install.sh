#!/bin/bash
apt-get install -y python3-pip
curl -sSL https://get.docker.com | sh
pip3 -v install docker-compose
pip3 install -f /root/install/requirements.txt
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
timedatectl set-timezone $(TIMEZONE}
echo "Install opencv, this will take some time"
apt install -y gnome-session gdm3

apt install -y build-essential cmake git pkg-config libgtk-3-dev \
libavcodec-dev libavformat-dev libswscale-dev libv4l-dev \
libxvidcore-dev libx264-dev libjpeg-dev libpng-dev libtiff-dev \
gfortran openexr libatlas-base-dev python3-dev python3-numpy \
libtbb2 libtbb-dev libdc1394-22-dev libopenexr-dev \
libgstreamer-plugins-base1.0-dev libgstreamer1.0-dev

mkdir /root/opencv_build && cd /root/opencv_build
git clone https://github.com/opencv/opencv.git

cd /root/opencv_build/opencv
mkdir -p build && cd build

cmake -D CMAKE_BUILD_TYPE=RELEASE \
-D CMAKE_INSTALL_PREFIX=/usr/local \
-D INSTALL_C_EXAMPLES=ON \
-D INSTALL_PYTHON_EXAMPLES=ON \
-D OPENCV_GENERATE_PKGCONFIG=ON \
-D OPENCV_EXTRA_MODULES_PATH=/root/opencv_build/opencv_contrib/modules \
-D BUILD_EXAMPLES=ON ..
echo "Installation finished, reboot now the system"

make j4
