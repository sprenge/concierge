FROM ubuntu:20.04
ARG FLASK
ARG FLASK_RESTFUL
ARG TIMEZONE
ARG REQUESTS

RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y install python3-pip
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata
RUN pip3 install Pillow
RUN pip3 install pyftpdlib
RUN pip3 install requests==${REQUESTS}
RUN pip3 install Flask==${FLASK}
RUN pip3 install Flask-RESTful==${FLASK_RESTFUL}
	
COPY ./ftp/ftpd/ftpd.py /

# startup
RUN ln -snf /usr/share/zoneinfo/$TIMEZONE /etc/localtime && echo $TIMEZONE > /etc/timezone
CMD python3 -u ftpd.py

EXPOSE 21 5101 30000-30009

