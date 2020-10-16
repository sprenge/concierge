FROM ubuntu 

RUN apt-get -y update
RUN apt-get -y install python3-pip
RUN pip3 install pyftpdlib
	

COPY ./ftpd.py /

# startup
CMD python3 ftpd.py

EXPOSE 21 30000-30009

