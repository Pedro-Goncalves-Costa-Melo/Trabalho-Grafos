import networkx as nx
import matplotlib.pyplot as plt

# Criar um multigrafo direcionado
G = nx.MultiDiGraph()

# Adicionar nós
G.add_node(0, tipo='depósito')
G.add_node(1, tipo='cliente')
G.add_node(2)
G.add_node(3)

# Adicionar arcos (vias de mão única)
G.add_edge(0, 1, custo=4, demanda=2, requer_serviço=True)
G.add_edge(1, 2, custo=3, demanda=0, requer_serviço=False)
G.add_edge(2, 3, custo=2, demanda=1, requer_serviço=True)
G.add_edge(3, 0, custo=5, demanda=0, requer_serviço=False)

# Gerar posições automáticas para os nós
pos = nx.spring_layout(G)

# Desenhar o grafo
plt.figure(figsize=(8, 6))
nx.draw_networkx_nodes(G, pos, node_size=700, node_color='lightblue')
nx.draw_networkx_labels(G, pos)

# Desenhar arestas com cor diferente se requer serviço
edge_colors = ['red' if data['requer_serviço'] else 'gray' for _, _, data in G.edges(data=True)]
nx.draw_networkx_edges(G, pos, edge_color=edge_colors, arrows=True)

# Adicionar rótulos de custo e demanda nas arestas
edge_labels = {(u, v): f"c: {d['custo']}, q: {d['demanda']}" for u, v, d in G.edges(data=True)}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

plt.title("Visualização do Grafo com Serviços e Demandas")
plt.axis('off')
plt.show()
