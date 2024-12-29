import asyncio
from topology_visualizer import TopologyVisualizer
from dhcp_discovery import DHCPDiscovery
from snmp_topology_mapper import SNMPTopologyMapper

iface = "eth0"
filename = "topology.html"

async def main():
    # discover DHCP server address
    dhcp_discovery = DHCPDiscovery(iface)
    server_address = dhcp_discovery.discover_dhcp()
    # stop if unable to discover DHCP server
    if server_address is None:
        return

    # map network topology using SNMP
    snmp_topology_mapper = SNMPTopologyMapper(server_address)
    (nodes, nodes_by_ip) = await snmp_topology_mapper.map()

    # visualize network topology
    topology_visualizer = TopologyVisualizer()
    topology_visualizer.visualize(nodes, nodes_by_ip, filename)
    

if __name__ == "__main__":
    asyncio.run(
        main()
    )
    