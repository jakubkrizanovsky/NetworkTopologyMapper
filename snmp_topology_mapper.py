from time import sleep
from scapy.all import *
import threading

class SNMPTopologyMapper:

    def __init__(self, iface, server_address):
        self.iface = iface
        self.server_address = server_address

    def test(self):
        t1 = threading.Thread(target=self.listen_snmp)
        t2 = threading.Thread(target=self.send_snmp_request)

        t1.start()
        sleep(1)
        t2.start()
        
        t1.join()
        t2.join()


    def listen_snmp(self):
        print("Listening...")
        sniff(prn=self.process_snmp_packet, iface=self.iface, filter=f"udp and port 161", count=2)


    def send_snmp_request(self):
        snmp_request = (
            IP(dst=self.server_address) /  # IP layer
            UDP(sport=161, dport=161) /  # UDP layer with SNMP default port 161
            SNMP(
                community="public",
                PDU=SNMPget(
                    varbindlist=[
                        SNMPvarbind(oid=ASN1_OID("1.3.6.1.2.1.4.21"))  # OID for ipRouteTable
                    ]
                )
            )
        )

        # Send the SNMP packet
        send(snmp_request)


    def process_snmp_packet(self, packet):
        if packet.haslayer(SNMP):
            print("SNMP Response Received:")
            packet.show()
            packet[SNMP].show()