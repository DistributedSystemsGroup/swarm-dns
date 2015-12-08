#!/usr/bin/python

import os
import logging
import pickle
import time

import swarm
import dnsupdate

pickle_db = '/var/lib/swarm-dns/data.pickle'

log = logging.getLogger('swarm-dns')

swarm_master = None
dns_updater = None


def new_record(docker_id, hostname, ip):
    dns_updater.add_a_record(hostname, ip)
    try:
        fp = open(pickle_db, "rb")
        data = pickle.load(fp)
        fp.close()
    except OSError:
        data = {}
    data[docker_id] = (hostname, ip)
    fp = open(pickle_db, "wb")
    pickle.dump(data, fp)
    fp.close()


def delete_record(docker_id):
    try:
        fp = open(pickle_db, "rb")
        data = pickle.load(fp)
        fp.close()
    except OSError:
        log.error("Pickled state not found, could not delete entry for container {}".format(docker_id))
        return
    if docker_id in data:
        hostname, ip = data[docker_id]
        dns_updater.delete_a_record(hostname, ip)
    else:
        log.error("Could not find Docker ID {}, cannot remove DNS entry".format(docker_id))


def manage_event(event):
    if event['status'] == "start":
        log.debug("Container started on host " + event['node']['Name'])
        try:
            info = swarm_master.inspect_container(event['id'])
        except ValueError:
            log.warning("Docker client cannot decode inspect answer, skipping")
            return
        retries = 3
        while info is None and retries > 0:
            info = swarm_master.inspect_container(event['id'])
            time.sleep(0.5)
        log.info("Container '{}' started with IP '{}' on host {}".format(info['hostname'], info['ip_address'], event['node']['Name']))
        new_record(event['id'], info['hostname'], info['ip_address'])
    elif event['status'] == "die":
        log.debug("Container died on host " + event['node']['Name'])
        log.info("Container '{}' died on host {}".format(event['id'], event['node']['Name']))
        delete_record(event['id'])
    return True


def main():
    global swarm_master, dns_updater
    logging.basicConfig()
    log.setLevel(logging.DEBUG)
    swarm_master_url = os.getenv("SWARM_MASTER", "tcp://localhost:2375")
    swarm_master = swarm.SwarmClient(swarm_master_url)
    dns_updater = dnsupdate.DDNSUpdater("m1", 'rndc.key', 'swarm.bigfoot.eurecom.fr')
    swarm_master.manage_event(manage_event)


if __name__ == "__main__":
    main()
