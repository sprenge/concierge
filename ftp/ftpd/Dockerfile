FROM ubuntu:18.04

RUN apt-get -y update
RUN apt-get -y install python3-pip
RUN pip3 install pyftpdlib
	
COPY ./ftp/ftpd/ftpd.py /

# startup
CMD python3 ftpd.py

EXPOSE 21 30000-30009

