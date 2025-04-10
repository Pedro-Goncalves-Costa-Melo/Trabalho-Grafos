import networkx as nx
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

    # Adiciona as arestas como duas direções para manter conectividade em grafo dirigido
    for chave in grafo["arestas"]:
        u, v = tuple(chave)
        G.add_edge(u, v)
        G.add_edge(v, u)

    for u, v in grafo["arcos"]:
        G.add_edge(u, v)

    stats = {
        "Quantidade de vértices": len(grafo["V"]),
        "Quantidade de arestas": len(grafo["arestas"]),
        "Quantidade de arcos": len(grafo["arcos"]),
        "Quantidade de vértices requeridos": len(grafo["VR"]),
        "Quantidade de arestas requeridas": len(grafo["ER"]),
        "Quantidade de arcos requeridos": len(grafo["AR"]),
        "Densidade do grafo": nx.density(G),
        "Componentes conectados": nx.number_weakly_connected_components(G),
        "Grau mínimo dos vértices": min(dict(G.degree()).values()),
        "Grau máximo dos vértices": max(dict(G.degree()).values()),
        "Intermediação": nx.betweenness_centrality(G),
        "Caminho médio": (
            nx.average_shortest_path_length(G) if nx.is_weakly_connected(G) else None
        ),
        "Diâmetro": (
            nx.diameter(G.to_undirected()) if nx.is_weakly_connected(G) else None
        ),
    }
    return stats


# === FLOYD-WARSHALL (opcional para distância/predecessores) ===
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
        if isinstance((u, v), frozenset) or isinstance((v, u), frozenset):
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
estat = estatisticas_grafo(grafo)

for k, v in estat.items():
    if isinstance(v, dict):  # para a intermediação
        print(f"{k}:")
        for subk, subv in v.items():
            print(f"  Nó {subk}: {subv}")
    else:
        print(f"{k}: {v}")
