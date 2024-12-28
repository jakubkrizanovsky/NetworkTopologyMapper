from dhcp_discovery import DHCPDiscovery

iface = "eth0"

if __name__ == "__main__":
    dhcp_discovery = DHCPDiscovery(iface)
    dhcp_discovery.discover_dhcp()
    print(dhcp_discovery.server_address)