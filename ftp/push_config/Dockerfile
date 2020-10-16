FROM ubuntu:18.04

RUN apt-get -y update
RUN apt-get -y install python3-pip
RUN pip3 install requests
	
COPY ./ftp/push_config/push_config.py /
COPY ./camera /camera

# startup
CMD python3 push_config.py


