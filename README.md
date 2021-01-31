# Introduction
Concierge is an enhanced Video Management System offering the following features:
* Central configuration of camera settings
* Central collection/viewing of recordings
* Collect motion triggers from cameras
* Video analytics on recordings
  * Motion detection
  * Shape detections (e.g. car, person, ...) based on a profile (e.g. selection of objects of interest)
  * Face detection / reocognition
  * Object comparison
  * Covered camera detection
  * Loitering
  * ...
* Data collection of analytics and visualization
* Classification of objects (unknown faces, unknown objects) : identifies these persons and objects
* Integration with Home Assistant (Home automation system)
  * Motion events reporting , global and per camera
  * Shape events reporting, global and per camera (e.g. person detected)
  * Event reporting of Object classification :
    * Unknown persons (faces)
    * Unknow objects (car)
    * Known objects/persons + roles (trusted person, own car, car of delivery company, ...)

---
**note**

Concierge is currently under development so not all of the above features are implemented yet.  Also, camera support is currently limited to Reolink RLC-410.

---
# Installation procedure
The current installation procedure is only guaranteed on Rasberry pi / ubuntu 20.4.  Open a terminal after installation

```bash
sudo -i
apt-get update
apt-get -y ugrade
apt-get -y install git
git clone https://github.com/sprenge/concierge.git
cd concierge
chmod +x install/install.sh
./install.sh
# be patient while concierge is installing
reboot
```
Make sure that your rasberry pi and cameras have a fixed IP address (most of the home routers/gateway foresee this feature)

Edit the .env file and change at least the following variables :
- CONCIERGE_IP_ADDRESS=\<IP address of your raspberry pi in your home network\>
- TIMEZONE=\<Your timezone\>

Other settings :
- ROOT_DIR : root directory used by concierge as storage

```bash
# start concierge
docker-compose up -d
# logs
docker-compose logs -f
# stop concierge
docker-compose down
```

Redirection of docker logs to syslog of the host machine : create /etc/docker/daemon.json and restart docker

```bash
{
  "log-driver": "syslog",
  "log-opts": {
    "syslog-address": "udp://192.168.1.59:514",
    "tag": "{{.Name}}"
  }
}
```

# Camera control

Open a browser and navigate to the following URL : http://<concierge ip>/admin
User / password : admin/12345678

Only the django admin interface is currently forseen for configuring cameras and look at recordings, a more enhanced interface will be foreseen in the future.