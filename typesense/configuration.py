from .exceptions import ConfigError


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


class Configuration(object):
    def __init__(self, config_dict):
        Configuration.validate_config_dict(config_dict)

        master_node_dict = config_dict.get('master_node', None)
        replica_node_dicts = config_dict.get('read_replica_nodes', [])

        self.master_node = Node(master_node_dict['host'], master_node_dict['port'],
                                master_node_dict['protocol'], master_node_dict['api_key'])

        self.read_replica_nodes = []
        for replica_node_dict in replica_node_dicts:
            self.read_replica_nodes.append(
                Node(replica_node_dict['host'], replica_node_dict['port'],
                     replica_node_dict['protocol'], replica_node_dict['api_key'])
            )

        self.timeout_seconds = config_dict.get('timeout_seconds', 1.0)

    @staticmethod
    def validate_config_dict(config_dict):
        master_node = config_dict.get('master_node', None)
        if not master_node:
            raise ConfigError('`master_node` is not defined.')

        if not Configuration.validate_node_fields(master_node):
            raise ConfigError('`master_node` must be a dictionary with the following required keys: '
                              'host, port, protocol, api_key')

        replica_nodes = config_dict.get('read_replica_nodes', [])
        for replica_node in replica_nodes:
            if not Configuration.validate_node_fields(replica_node):
                raise ConfigError('`read_replica_nodes` entry be a dictionary with the following required keys: '
                                  'host, port, protocol, api_key')

    @staticmethod
    def validate_node_fields(node):
        expected_fields = {'host', 'port', 'protocol', 'api_key'}
        return expected_fields.issubset(node)
