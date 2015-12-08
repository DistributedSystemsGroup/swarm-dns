# swarm-dns
A small daemon to keep a Bind DNS server in sync with containers created in Docker Swarm.

To use:

1. copy a `rndc.key` file containing the DDNS key from bind in this directory
2. customize the `build.sh` file to set the right Docker tags for your environment
3. run `build.sh` to build and push the Docker image containing the RNDC key (do not push to the public docker hub!)
4. customize the `start.sh` script: set the Swarm manager location, volume path and image name
5. run `start.sh` and enjoy your fully qualified container names

`start.sh` will run `swarm-dns` in a container.

Launch containers by giving them hostnames (the -h option of `docker run`).

Please note:

This script is work-in-progress and should be used with caution.
You will need to modify `main.py` to set the DNS server IP and domain to use for the containers.

Since Docker reports only the ID of the container in the event stream, `swarm-dns` needs to keep the association between ID, IP and hostname, so that it can remove the entry from the DNS when the container is destroyed.
This means that `swarm-dns` has state and it makes it much more complex and unreliable. The state can go out of sync if events happen while `swarm-dns` is down or if the state file is lost.

Nothing should prevent `swarm-dns` from working with a Docker Engine instance instead of a full Swarm.

Pull requests are more than welcome!