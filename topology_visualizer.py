from pyvis.network import Network

net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")

net.add_node(0, label='a')
net.add_node(1, label='b')
net.add_edge(0, 1)

net.show("test.html", notebook=False)