import asyncio
from pysnmp.hlapi.v3arch.asyncio import *

from topology_node import TopologyNode



class SNMPTopologyMapper:

    def __init__(self, start_address:str):
        self.searched_ips:list = []
        self.waiting_ips:list = [start_address]
        self.nodes:list = []
        self.nodes_by_name:dict = {}

    async def map(self) -> list:
        snmpEngine = SnmpEngine()
        while len(self.waiting_ips) > 0:
            await self.search(snmpEngine, self.waiting_ips.pop(0))
            print(self.waiting_ips)
        
        return self.nodes

    async def search(self, snmpEngine:SnmpEngine, ipAddress:str):
        print(f"Searching: {ipAddress}")

        self.searched_ips.append(ipAddress)

        sys_name = await self.get_sys_name(snmpEngine, ipAddress)
        if sys_name is None:
            node = TopologyNode(ipAddress)
            self.nodes.append(node)
            return
        
        print(sys_name)
        node = self.nodes_by_name.get(sys_name)
        if node is not None:
            node.ip_addresses.append(ipAddress)
            print("Already searched, skipping")
            return
        
        node = TopologyNode(ipAddress)
        self.nodes.append(node)
        self.nodes_by_name[sys_name] = node
        node.sys_name = sys_name

        print("Neighbors:")

        neighbors = await self.get_neighbors(snmpEngine, ipAddress)

        for neighbor_ip in neighbors:
            print(neighbor_ip)
            node.neighbors.append(neighbor_ip)
            if not neighbor_ip in self.searched_ips and not neighbor_ip in self.waiting_ips:
                self.waiting_ips.append(neighbor_ip)

        

    async def get_sys_name(self, snmpEngine:SnmpEngine, ipAddress:str) -> str:
        errorIndication, errorStatus, errorIndex, varBindTable = await getCmd(
                snmpEngine,
                CommunityData("psipub"),
                await UdpTransportTarget.create((ipAddress, 161)),
                ContextData(),
                ObjectType(ObjectIdentity("1.3.6.1.2.1.1.5.0")), #sysName
                lexicographicMode=False
        )

        if not errorIndication:
            return varBindTable[0][1].prettyPrint()
        else:
            print(errorIndication)
            return None
        
    
    async def get_neighbors(self, snmpEngine:SnmpEngine, ipAddress:str) -> list:
        neighbors = []

        items = walkCmd(
                snmpEngine,
                CommunityData("psipub"),
                await UdpTransportTarget.create((ipAddress, 161)),
                ContextData(),
                ObjectType(ObjectIdentity("1.3.6.1.2.1.4.21.1.7")), #ipRouteNextHop
                lexicographicMode=False
        )

        async for item in items:
            errorIndication, errorStatus, errorIndex, varBindTable = item
            if errorIndication:
                print(errorIndication)
                break
            elif errorStatus:
                print(
                    f"{errorStatus.prettyPrint()} at {item[int(errorIndex) - 1][0] if errorIndex else '?'}"
                )
            else:
                ip = varBindTable[0][1].prettyPrint()
                neighbors.append(ip)

        return neighbors


if __name__ == "__main__":
    snmp_topology_mapper:SNMPTopologyMapper = SNMPTopologyMapper("10.0.1.1")
    asyncio.run(
        snmp_topology_mapper.map()
    )