class Node(object):
    def __init__(self, host, port, protocol, api_key):
        self.host = host
        self.port = port
        self.protocol = protocol
        self.api_key = api_key

    def url(self):
        return '{0}://{1}:{2}'.format(self.protocol, self.host, self.port)

    def initialized(self):
        return self.host is not None and self.port is not None and \
               self.protocol is not None and self.api_key is not None


master_node = Node(host=None, port=8108, protocol='http', api_key=None)

read_replica_nodes = []

timeout_seconds = 1
