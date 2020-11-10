FROM ubuntu:18.04
ARG FLASK
ARG FLASK_RESTFUL

RUN apt-get -y update
RUN apt-get -y install python3-pip
RUN pip3 install requests
RUN pip3 install Flask==${FLASK}
RUN pip3 install Flask-RESTful==${FLASK_RESTFUL}
	
COPY ./camera/brand/reolink/recording.py /

# startup
CMD python3 -u recording.py

EXPOSE 5102

