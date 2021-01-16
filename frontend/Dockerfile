FROM ubuntu:20.04

RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get update
RUN apt-get -y install python3-pip
RUN apt-get -y install python3.8-dev
RUN apt-get update
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata
RUN apt-get -y install npm
RUN npm install -g angular-http-server

COPY ./frontend /

# startup
CMD /usr/local/bin/angular-http-server

EXPOSE 8080
