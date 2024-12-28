from dhcp_discovery import DHCPDiscovery
from snmp_topology_mapper import SNMPTopologyMapper

iface = "eth0"

if __name__ == "__main__":
    dhcp_discovery = DHCPDiscovery(iface)
    server_address = dhcp_discovery.discover_dhcp()
    print(server_address)

    snmp_topology_mapper = SNMPTopologyMapper(iface, server_address)
    snmp_topology_mapper.test()