import asyncio
from dhcp_discovery import DHCPDiscovery
from snmp_topology_mapper import SNMPTopologyMapper

iface = "eth0"

async def main():
    dhcp_discovery = DHCPDiscovery(iface)
    server_address = dhcp_discovery.discover_dhcp()
    print(server_address)

    snmp_topology_mapper = SNMPTopologyMapper(server_address)
    await snmp_topology_mapper.map()
    

if __name__ == "__main__":
    asyncio.run(
        main()
    )
    