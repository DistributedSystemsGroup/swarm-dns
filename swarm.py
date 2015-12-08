import docker
import docker.errors

try:
    from kazoo.client import KazooClient
except ImportError:
    print("Kazoo library not found, Zookeeper connect URLs will not work")
    KazooClient = None


class SwarmClient:
    def __init__(self, swarm_url):
        assert isinstance(swarm_url, str)
        self.cli = None
        self._connect(swarm_url)
        assert self.cli is not None

    def _connect(self, swarm_url):
        if swarm_url.startswith('tcp://'):
            self._connect_tcp(swarm_url)
        elif swarm_url.startswith('zk://'):
            self._connect_zookeeper(swarm_url)
        else:
            print("Unknown connection URL schema")
            return

    def _connect_zookeeper(self, zk_url):
        """
        Find the active Swarm master using Zookeeper
        """
        aux = zk_url[len('zk://'):]
        zk_hosts = aux.split('/')[0]
        path = aux[aux.find('/'):] + '/docker/swarm/leader'
        zk = KazooClient(hosts=zk_hosts)
        zk.start()
        master, stat = zk.get(path)
        zk.stop()
        self._connect_tcp('tcp://' + master.decode('ascii'))

    def _connect_tcp(self, tcp_url):
        self.cli = docker.Client(base_url=tcp_url)
        print("Connected to Swarm at {}".format(tcp_url))

    def manage_event(self, callback):
        for event in self.cli.events(decode=True):
            if not callback(event):
                break

    def inspect_container(self, docker_id) -> dict:
        try:
            docker_info = self.cli.inspect_container(container=docker_id)
        except docker.errors.APIError:
            return None
        info = {
            "ip_address": docker_info["NetworkSettings"]["IPAddress"],
            "docker_id": docker_id,
            "hostname": docker_info["Config"]["Hostname"]
        }
        if docker_info["State"]["Running"]:
            info["state"] = "running"
            info["running"] = True
        elif docker_info["State"]["Paused"]:
            info["state"] = "paused"
            info["running"] = True
        elif docker_info["State"]["Restarting"]:
            info["state"] = "restarting"
            info["running"] = True
        elif docker_info["State"]["OOMKilled"]:
            info["state"] = "killed"
            info["running"] = False
        elif docker_info["State"]["Dead"]:
            info["state"] = "killed"
            info["running"] = False
        else:
            info["state"] = "unknown"
            info["running"] = False
        return info
