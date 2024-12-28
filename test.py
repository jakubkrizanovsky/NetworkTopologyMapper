from time import sleep
from scapy.all import *
import threading

iface = "eth0"
server_address = None

def mac_to_bytes(mac_addr: str) -> bytes:
    """ Converts a MAC address string to bytes.
    """
    return int(mac_addr.replace(":", ""), 16).to_bytes(6, "big")

def check_dhcp_packet(packet):
    print("Receved packet")

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
            server_address = value
    
    print(f"Server address: {server_address}")


def listen_dhcp():
    print("Listening...")
    # Make sure it is DHCP with the filter options
    sniff(prn=check_dhcp_packet, iface=iface, filter="port 68 and port 67", count=2)

def discover_dhcp():
    
    print("Sending DHCP discover...")
    fam,mac = get_if_raw_hwaddr(iface)

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
    sendp(packet, iface=iface, verbose=False)


if __name__ == "__main__":
    t1 = threading.Thread(target=listen_dhcp)
    t2 = threading.Thread(target=discover_dhcp)

    t1.start()
    sleep(1)
    t2.start()
    
    t1.join()
    t2.join()