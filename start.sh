#!/usr/bin/env bash

export SWARM_MASTER=zk://bf1:2181,bf5:2181,bf11:2181/swarm

VERSION=`cat VERSION`

docker -H bf1:2380 run -d -v /mnt/cephfs/docker-volumes/swarm-dns:/var/lib/swarm-dns --restart=always --name swarm-dns -e SWARM_MASTER=$SWARM_MASTER 10.1.0.1:5000/venza/swarm-dns:$VERSION
