from pyvis.network import Network

from topology_node import TopologyNode

class TopologyVisualizer:
    def __init__(self):
        self.net = Network()

    def visualize(self, nodes:list, nodes_by_ip:dict, filename:str):
        node:TopologyNode
        for node in nodes:
            if node.sys_name is not None:
                self.net.add_node(node.node_id, node.sys_name)
            else:
                self.net.add_node(node.node_id)

        for node in nodes:
            for neighbor_ip in node.neighbors:
                neighbor = nodes_by_ip[neighbor_ip]
                self.net.add_edge(node.node_id, neighbor.node_id)

        self.net.show(filename, notebook=False)



