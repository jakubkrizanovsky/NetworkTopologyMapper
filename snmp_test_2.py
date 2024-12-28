import asyncio
from pysnmp.hlapi.v3arch.asyncio import *

searched = []
waiting = []

async def run():
    waiting.append("10.0.1.1")
    snmpEngine = SnmpEngine()
    while len(waiting) > 0:
        await search(snmpEngine, waiting.pop(0))

async def search(snmpEngine:SnmpEngine, ipAddress:str):
    print(f"Searching: {ipAddress}")

    searched.append(ipAddress)
    objects = walkCmd(
            snmpEngine,
            CommunityData("psipub"),
            await UdpTransportTarget.create((ipAddress, 161)),
            ContextData(),
            ObjectType(ObjectIdentity("1.3.6.1.2.1.4.21.1.1")),
            lexicographicMode=False
    )

    async for item in objects:
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

            if not ip in searched and not ip in waiting:
                waiting.append(ip)

        


if __name__ == "__main__":
    asyncio.run(
        run()
    )