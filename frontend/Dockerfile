FROM ubuntu:20.04

RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y install python3-pip
RUN apt-get -y install python3.8-dev

COPY ./frontend /

# startup
CMD python3 -u main.py
RUN echo "192.168.1.59 concierge" >> /etc/hosts

EXPOSE 5200
