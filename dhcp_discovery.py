from time import sleep
from scapy.all import *
import threading

class DHCPDiscovery:

    def __init__(self, iface):
        self.iface = iface
        self.server_address = None

    
    def discover_dhcp(self):
        t1 = threading.Thread(target=self.listen_dhcp)
        t2 = threading.Thread(target=self.send_dhcp_discover)

        print("Starting DHCP discovery...")
        t1.start()
        sleep(1)
        t2.start()
        
        t1.join()
        t2.join()

        if self.server_address is not None:
            print("DHCP discovery complete")
        else:
            print("Could not discover DHCP server")

        return self.server_address


    def listen_dhcp(self):
        print("Listening for DHCP packets...")
        sniff(prn=self.process_dhcp_packet, iface=self.iface, filter="port 68 and port 67", count=2, timeout=5)


    def send_dhcp_discover(self):
        
        # get interface MAC address
        fam,mac = get_if_raw_hwaddr(self.iface)

        packet = (
            Ether(dst="ff:ff:ff:ff:ff:ff") /
            IP(src="0.0.0.0", dst="255.255.255.255") /
            UDP(sport=68, dport=67) /
            BOOTP(
                chaddr=mac,
                xid=random.randint(1, 2**32-1),
            ) /
            DHCP(options=[("message-type", "discover"), "end"])
        )

        print("Sending DHCP discover packet...")
        sendp(packet, iface=self.iface, verbose=False)


    def process_dhcp_packet(self, packet):
        bootp_operation = packet[BOOTP].op
        # skip everything except bootreply operation
        if(bootp_operation != 2):
            return

        # get the DHCP options
        dhcp_options = packet[DHCP].options
        for item in dhcp_options:
            try:
                label, value = item
            except ValueError:
                continue
            if label == "server_id":
                self.server_address = value
        
        print(f"DHCP Server address: {self.server_address}")


    def mac_to_bytes(mac_addr: str) -> bytes:
        return int(mac_addr.replace(":", ""), 16).to_bytes(6, "big")
