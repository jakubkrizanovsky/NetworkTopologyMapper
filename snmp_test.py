import asyncio
from pysnmp.smi import builder, view
from pysnmp.hlapi.v3arch.asyncio import *


async def run(varBinds, base_oid:ObjectIdentity):
    snmpEngine = SnmpEngine()
    while True:
        errorIndication, errorStatus, errorIndex, varBindTable = await bulkCmd(
            snmpEngine,
            CommunityData("psipub"),
            await UdpTransportTarget.create(("10.0.1.1", 161)),
            ContextData(),
            0,
            10,
            *varBinds,
        )

        if errorIndication:
            print(errorIndication)
            break
        elif errorStatus:
            print(
                f"{errorStatus.prettyPrint()} at {varBinds[int(errorIndex) - 1][0] if errorIndex else '?'}"
            )
        else:
            for varBind in varBindTable:
                oid: ObjectIdentity = varBind[0]
                if not base_oid.getOid().isPrefixOf(oid.getOid()):
                    # Stop if OID is outside the target table
                    print("End of routing table reached.")
                    return
                print(oid.getOid())
                

        varBinds = varBindTable
        if not varBindTable or isEndOfMib(varBinds):
            break
    return

if __name__ == "__main__":
    # Create a MIB builder
    mib_builder = builder.MibBuilder()

    # Initialize the MIB view controller
    mib_view_controller = view.MibViewController(mib_builder)

    # Load default MIBs (optional)
    mib_builder.loadModules()
    oid = ObjectIdentity("1.3.6.1.2.1.4.21.1.1")
    oid.resolveWithMib(mib_view_controller)
    print(oid.getLabel())
    asyncio.run(
        run([ObjectType(oid)], oid)
    )