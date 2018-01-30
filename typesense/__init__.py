class Node(object):
    def __init__(self):
        self.host = None
        self.port = None
        self.protocol = None
        self.api_key = None

    def url(self):
        return self.protocol + '://' + self.host + ':' + str(self.port)

master_node = Node()

read_replica_nodes = []

timeout_seconds = 1

from collections import Collections