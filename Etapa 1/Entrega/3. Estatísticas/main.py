import networkx as nx
import matplotlib.pyplot as plt
import numpy as np


# === LEITURA ===
def ler_grafo(caminho_arquivo):
    with open(caminho_arquivo, "r") as f:
        linhas = [
            linha.strip() for linha in f if linha.strip() and not linha.startswith("#")
        ]

    num_nos = int(linhas[0])
    deposito = int(linhas[1])
    capacidade = int(linhas[2])

    V = set(range(num_nos))
    VR = set(map(int, linhas[3].split()))

    ER, AR = set(), set()
    arestas, arcos = {}, {}

    idx = 4
    secao = "arestas_servico"
    while idx < len(linhas):
        linha = linhas[idx]
        u, v, custo, demanda = map(int, linha.split())

        if secao == "arestas_servico":
            chave = frozenset({u, v})
            arestas[chave] = {
                "custo": custo,
                "demanda": demanda,
                "requer_serviço": demanda > 0,
            }
            if demanda > 0:
                ER.add(chave)
            secao = "arcos_servico"

        elif secao == "arcos_servico":
            chave = (u, v)
            arcos[chave] = {
                "custo": custo,
                "demanda": demanda,
                "requer_serviço": demanda > 0,
            }
            if demanda > 0:
                AR.add(chave)
            if len(arcos) == 2:
                secao = "arestas_sem_servico"

        elif secao == "arestas_sem_servico":
            chave = frozenset({u, v})
            arestas[chave] = {
                "custo": custo,
                "demanda": demanda,
                "requer_serviço": False,
            }
            secao = "arcos_sem_servico"

        elif secao == "arcos_sem_servico":
            chave = (u, v)
            arcos[chave] = {"custo": custo, "demanda": demanda, "requer_serviço": False}
        idx += 1

    return {
        "V": V,
        "deposito": deposito,
        "capacidade": capacidade,
        "VR": VR,
        "ER": ER,
        "AR": AR,
        "arestas": arestas,
        "arcos": arcos,
    }


# === ESTATÍSTICAS ===
def estatisticas_grafo(grafo):
    G = nx.MultiDiGraph()
    G.add_nodes_from(grafo["V"])
    for u, v in grafo["arestas"]:
        G.add_edges_from([(u, v), (v, u)])
    for u, v in grafo["arcos"]:
        G.add_edge(u, v)

    stats = {
        "Vértices": len(grafo["V"]),
        "Arestas": len(grafo["arestas"]),
        "Arcos": len(grafo["arcos"]),
        "Vértices Requeridos": len(grafo["VR"]),
        "Arestas Requeridas": len(grafo["ER"]),
        "Arcos Requeridos": len(grafo["AR"]),
        "Densidade": nx.density(G),
        "Componentes": nx.number_weakly_connected_components(G),
        "Grau mínimo": min(dict(G.degree()).values()),
        "Grau máximo": max(dict(G.degree()).values()),
        "Intermediação": nx.betweenness_centrality(G),
        "Caminho médio": (
            nx.average_shortest_path_length(G) if nx.is_weakly_connected(G) else None
        ),
        "Diâmetro": (
            nx.diameter(G.to_undirected()) if nx.is_weakly_connected(G) else None
        ),
    }
    return stats


# === FLOYD-WARSHALL ===
def floyd_warshall(grafo):
    n, INF = len(grafo["V"]), np.inf
    dist = np.full((n, n), INF)
    pred = np.full((n, n), -1)
    for v in grafo["V"]:
        dist[v][v] = 0
        pred[v][v] = v
    for (u, v), d in {**grafo["arestas"], **grafo["arcos"]}.items():
        dist[u][v] = d["custo"]
        pred[u][v] = u
        if isinstance(u, set):
            dist[v][u] = d["custo"]
            pred[v][u] = v
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i, k] + dist[k, j] < dist[i, j]:
                    dist[i, j] = dist[i, k] + dist[k, j]
                    pred[i, j] = pred[k, j]
    return dist, pred


# === EXECUÇÃO PRINCIPAL ===
grafo = ler_grafo("entrada.txt")
# visualizar_grafo(grafo)
estat = estatisticas_grafo(grafo)
for k, v in estat.items():
    print(f"{k}: {v}")
dist, pred = floyd_warshall(grafo)
print("Distâncias:\n", dist)
print("Predecessores:\n", pred)
