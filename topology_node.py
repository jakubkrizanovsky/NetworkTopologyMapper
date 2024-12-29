class TopologyNode:

    id_counter = 0

    def __init__(self, ip_address:str):
        self.node_id = TopologyNode.id_counter
        TopologyNode.id_counter += 1

        self.sys_name = None
        self.ip_addresses = [ip_address]
        self.neighbors = []