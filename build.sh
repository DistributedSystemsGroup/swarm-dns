#!/usr/bin/env bash

VERSION=`cat VERSION`

sudo docker build -t swarm-dns:$VERSION .
sudo docker tag -f swarm-dns:$VERSION 10.1.0.1:5000/venza/swarm-dns:$VERSION
sudo docker push 10.1.0.1:5000/venza/swarm-dns:$VERSION
