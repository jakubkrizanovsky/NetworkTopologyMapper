from time import sleep
from scapy.all import *
import threading

iface = "eth0"

def mac_to_bytes(mac_addr: str) -> bytes:
    """ Converts a MAC address string to bytes.
    """
    return int(mac_addr.replace(":", ""), 16).to_bytes(6, "big")

def print_packet(packet):
    print("Receved packet:")
    packet.show()

    # initialize these variables to None at first
    target_mac, requested_ip, hostname, vendor_id = [None] * 4
    # get the MAC address of the requester
    if packet.haslayer(Ether):
        target_mac = packet.getlayer(Ether).src
    # get the DHCP options
    dhcp_options = packet[DHCP].options
    for item in dhcp_options:
        try:
            label, value = item
        except ValueError:
            continue
        if label == 'requested_addr':
            # get the requested IP
            requested_ip = value
        elif label == 'hostname':
            # get the hostname of the device
            hostname = value.decode()
        elif label == 'vendor_class_id':
            # get the vendor ID
            vendor_id = value.decode()
    #if target_mac and vendor_id and hostname and requested_ip:
    # if all variables are not None, print the device details
    time_now = time.strftime("[%Y-%m-%d - %H:%M:%S]")
    print(f"{time_now} : {target_mac}  -  {hostname} / {vendor_id} requested {requested_ip}")


def listen_dhcp():
    print("listening")
    # Make sure it is DHCP with the filter options
    sniff(prn=print_packet, iface="eth0", filter="port 68 and port 67", count=2)

def discover_dhcp():
    print("sending discover")
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
    sendp(packet, iface="eth0", verbose=False)


if __name__ == "__main__":
    t1 = threading.Thread(target=listen_dhcp)
    t2 = threading.Thread(target=discover_dhcp)
    t1.start()

    sleep(1)

    t2.start()
    
    t1.join()
    t2.join()