FROM ubuntu:20.04

RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y install python3-pip
RUN apt-get -y install sudo
RUN apt-get -y install curl

RUN echo "deb https://repos.influxdata.com/ubuntu bionic stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
RUN curl -sL https://repos.influxdata.com/influxdb.key | sudo apt-key add -
RUN apt-get update


COPY ./influx/run.sh /
RUN chmod +x /run.sh
RUN apt-get install influxdb


# COPY ./influx/influxdb.conf /etc/influxdb/influxdb.conf
ENV PRE_CREATE_DB concierge

# HTTP API
EXPOSE 8086
EXPOSE 8083

CMD ["/run.sh"]
