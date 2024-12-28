from dataclasses import dataclass

@dataclass
class TopologyNode:
    mac_address:str
    ip_addresses:list
    neighbors:list