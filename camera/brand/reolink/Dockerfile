FROM ubuntu:20.04
ARG FLASK
ARG FLASK_RESTFUL

RUN apt-get -y update
RUN apt-get -y install python3-pip
RUN pip3 install requests
RUN pip3 install Flask==${FLASK}
RUN pip3 install Flask-RESTful==${FLASK_RESTFUL}
	
COPY ./camera/brand/reolink/main.py /
COPY ./camera/brand/reolink/recording.py /
COPY ./camera/brand/reolink/login.py /
COPY ./camera/brand/reolink/reoconfig.py /
COPY ./camera/brand/reolink/configure.py /

# startup
CMD python3 -u main.py

EXPOSE 5102

