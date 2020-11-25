FROM ubuntu:20.04
ARG FLASK
ARG FLASK_RESTFUL

RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y install python3-pip
RUN pip3 install requests
RUN pip3 install Flask
RUN pip3 install Flask-RESTful==${FLASK_RESTFUL}
	
COPY ./motion/main.py /

# startup
CMD python3 -u main.py

EXPOSE 5104

