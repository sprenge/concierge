FROM ubuntu:20.04
ARG FLASK
ARG FLASK_RESTFUL

RUN apt-get -y update
RUN apt-get -y install python3-pip
RUN pip3 install pyftpdlib
RUN pip3 install requests
RUN pip3 install Flask
RUN pip3 install Flask-RESTful==${FLASK_RESTFUL}
	
COPY ./ftp/ftpd/ftpd.py /

# startup
CMD python3 -u ftpd.py

EXPOSE 21 5101 30000-30009

