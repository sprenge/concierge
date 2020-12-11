FROM ubuntu:18.04
ARG TIMEZONE

RUN apt-get -y update
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata
RUN apt-get -y install python3-pip
RUN pip3 install requests
RUN pip3 install schedule
	
COPY ./scheduler/scheduler.py /
COPY ./scheduler/clean_recordings.py /

# startup
CMD python3 -u scheduler.py


