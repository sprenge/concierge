FROM ubuntu:20.04
ARG FLASK
ARG FLASK_RESTFUL
ARG TIMEZONE
ARG REQUESTS

RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y install python3-pip
RUN apt-get -y install python3.8-dev
RUN apt-get update
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata
RUN apt install -y libopencv-dev python3-opencv
RUN pip3 install opencv-contrib-python
RUN pip3 install requests==${REQUESTS}
RUN pip3 install Flask==${FLASK}
RUN pip3 install Flask-RESTful==${FLASK_RESTFUL}
RUN pip3 install cmake
RUN pip3 install dlib
RUN pip3 install face-recognition==1.3.0
RUN pip3 install face-recognition-models==0.3.0
RUN pip3 install Pillow

COPY ./detect_shape /

# startup
RUN ln -snf /usr/share/zoneinfo/$TIMEZONE /etc/localtime && echo $TIMEZONE > /etc/timezone
CMD python3 -u main.py

EXPOSE 5103
EXPOSE 5105
