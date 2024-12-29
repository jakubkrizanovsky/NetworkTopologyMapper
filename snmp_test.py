import asyncio
from pysnmp.hlapi.v3arch.asyncio import *



class SNMPTopologyMapper:

    def __init__(self, start_address:str):
        self.searched_ips:list = []
        self.waiting_ips:list = [start_address]
        self.nodes:list = []

    async def map(self):
        snmpEngine = SnmpEngine()
        while len(self.waiting_ips) > 0:
            await self.get_neighbors(snmpEngine, self.waiting_ips.pop(0))
        
    
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
                print(varBindTable[0][0])
                print(varBindTable[0][1].prettyPrint())

        return neighbors


if __name__ == "__main__":
    snmp_topology_mapper:SNMPTopologyMapper = SNMPTopologyMapper("10.0.1.1")
    asyncio.run(
        snmp_topology_mapper.map()
    )