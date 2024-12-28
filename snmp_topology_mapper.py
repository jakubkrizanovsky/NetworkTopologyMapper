import asyncio
from pysnmp.hlapi.v3arch.asyncio import *

from topology_node import TopologyNode



class SNMPTopologyMapper:

    def __init__(self, start_address:str):
        self.searched_ips:list = []
        self.waiting_ips:list = [start_address]
        self.nodes:list = []

    async def map(self):
        snmpEngine = SnmpEngine()
        while len(self.waiting_ips) > 0:
            await self.search(snmpEngine, self.waiting_ips.pop(0))

    async def search(self, snmpEngine:SnmpEngine, ipAddress:str):
        print(f"Searching: {ipAddress}")

        self.searched_ips.append(ipAddress)

        #node = TopologyNode()

        print(await self.get_display_name(snmpEngine, ipAddress))
        

        print("Neighbors:")
        route_items = walkCmd(
                snmpEngine,
                CommunityData("psipub"),
                await UdpTransportTarget.create((ipAddress, 161)),
                ContextData(),
                ObjectType(ObjectIdentity("1.3.6.1.2.1.4.21.1.1")), #ipRouteDest
                lexicographicMode=False
        )

        async for item in route_items:
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
                print(ip)

                if not ip in self.searched_ips and not ip in self.waiting_ips:
                    self.waiting_ips.append(ip)

    async def get_display_name(self, snmpEngine:SnmpEngine, ipAddress:str) -> str:
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
            return None


if __name__ == "__main__":
    snmp_topology_mapper:SNMPTopologyMapper = SNMPTopologyMapper("10.0.1.1")
    asyncio.run(
        snmp_topology_mapper.map()
    )