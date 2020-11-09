FROM ubuntu:18.04

RUN apt-get -y update
RUN apt-get -y install python3-pip
RUN pip3 install Flask==1.1.2
RUN pip3 install Flask-RESTful==0.3.8
	
COPY ./scheduler/scheduler.py /

# startup
CMD python3 -u scheduler.py

EXPOSE 5100

