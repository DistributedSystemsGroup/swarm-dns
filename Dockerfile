FROM python:3.4-onbuild

MAINTAINER Daniele Venzano <venza@brownhat.org>

RUN mkdir /opt/swarm-dns
ADD . /opt/swarm-dns

WORKDIR /opt/swarm-dns

RUN mkdir /var/lib/swarm-dns

CMD ["python", "./main.py"]
