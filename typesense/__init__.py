class Node(object):
    def __init__(self):
        self.host = None
        self.port = None
        self.protocol = None
        self.api_key = None

    def url(self):
        return '{0}://{1}:{2}'.format(self.protocol, self.host, self.port)

    def initialized(self):
        return self.host is not None and self.port is not None and self.protocol is not None and \
               self.api_key is not None

master_node = Node()

read_replica_nodes = []

timeout_seconds = 1

from collections import Collections