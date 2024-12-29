import asyncio
from pysnmp.hlapi.v3arch.asyncio import *

from topology_node import TopologyNode


class SNMPTopologyMapper:

    def __init__(self, start_address:str):
        self.snmp_engine = SnmpEngine()
        self.searched_ips:list = []
        self.waiting_ips:list = [start_address]
        self.nodes:list = []
        self.nodes_by_ip:dict = {}

    async def map(self) -> tuple:
        while len(self.waiting_ips) > 0:
            await self.search(self.waiting_ips.pop(0))
            print(f"Waiting IPs: {self.waiting_ips}")
        
        return self.nodes, self.nodes_by_ip

    async def search(self, searched_ip:str):
        print(f"Searching: {searched_ip}")

        node = TopologyNode([searched_ip])
        self.nodes.append(node)

        # try get sysname from node using snmp
        sys_name = await self.get_sys_name(searched_ip)
        if sys_name is None: # cannot reach node via snmp - stop asking
            self.nodes_by_ip[searched_ip] = node
            return
        
        node.sys_name = sys_name
        print(f"Sys name: {sys_name}")

        ip_addresses = await self.get_ip_addresses(searched_ip)
        node.ip_addresses = ip_addresses
        print(f"IP adresses: {ip_addresses}")

        for ip_address in ip_addresses:
            self.nodes_by_ip[ip_address] = node

        self.searched_ips += ip_addresses

        neighbors = await self.get_neighbors(searched_ip)
        print(f"Neighbors: {neighbors}")

        for neighbor_ip in neighbors:
            if not neighbor_ip in node.ip_addresses and not neighbor_ip in node.neighbors:
                node.neighbors.append(neighbor_ip)
            if not neighbor_ip in self.searched_ips and not neighbor_ip in self.waiting_ips:
                self.waiting_ips.append(neighbor_ip)

        

    async def get_sys_name(self, searched_ip:str) -> str:
        errorIndication, errorStatus, errorIndex, varBindTable = await getCmd(
                self.snmp_engine,
                CommunityData("psipub"),
                await UdpTransportTarget.create((searched_ip, 161)),
                ContextData(),
                ObjectType(ObjectIdentity("1.3.6.1.2.1.1.5.0")), #sysName
                lexicographicMode=False
        )

        if not errorIndication:
            return varBindTable[0][1].prettyPrint()
        else:
            print(errorIndication)
            return None
        

    async def get_ip_addresses(self, searched_ip:str) -> list:
        addresses = []

        items = walkCmd(
                self.snmp_engine,
                CommunityData("psipub"),
                await UdpTransportTarget.create((searched_ip, 161)),
                ContextData(),
                ObjectType(ObjectIdentity("1.3.6.1.2.1.4.20.1.1")), #ipAdEntAddr
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
                addresses.append(ip)

        return addresses
        
    
    async def get_neighbors(self, searched_ip:str) -> list:
        neighbors = []

        items = walkCmd(
                self.snmp_engine,
                CommunityData("psipub"),
                await UdpTransportTarget.create((searched_ip, 161)),
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