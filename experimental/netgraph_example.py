import matplotlib.pyplot as plt
import networkx as nx
from netgraph import InteractiveGraph

g = nx.house_x_graph()

edge_color = dict()
for ii, edge in enumerate(g.edges):
    edge_color[edge] = 'tab:gray' if ii%2 else 'tab:orange'

node_color = dict()
for node in g.nodes:
    node_color[node] = 'tab:red' if node%2 else 'tab:blue'

fig, ax = plt.subplots(figsize=(10, 10))

plot_instance = InteractiveGraph(
    g, node_size=5, node_color=node_color,
    node_labels=True, node_label_offset=0.1, node_label_fontdict=dict(size=20),
    edge_color=edge_color, edge_width=2,
    arrows=True, ax=ax)

plt.show()