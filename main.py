import asyncio
from topology_visualizer import TopologyVisualizer
from dhcp_discovery import DHCPDiscovery
from snmp_topology_mapper import SNMPTopologyMapper

iface = "eth0"
filename = "topology.html"

async def main():
    dhcp_discovery = DHCPDiscovery(iface)
    server_address = dhcp_discovery.discover_dhcp()
    print(server_address)

    snmp_topology_mapper = SNMPTopologyMapper(server_address)
    nodes = await snmp_topology_mapper.map()

    topology_visualizer = TopologyVisualizer()
    topology_visualizer.visualize(nodes, filename)
    

if __name__ == "__main__":
    asyncio.run(
        main()
    )
    