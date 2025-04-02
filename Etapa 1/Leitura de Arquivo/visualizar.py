import networkx as nx
import matplotlib.pyplot as plt


def ler_grafo_para_visualizacao(caminho_arquivo):
    with open(caminho_arquivo, "r") as f:
        linhas = []
        for linha in f:
            linha = linha.strip()
            if linha and not linha.startswith("#"):
                linhas.append(linha)

    num_nos = int(linhas[0])
    deposito = int(linhas[1])
    capacidade = int(linhas[2])

    V = set(range(num_nos))
    VR = set(map(int, linhas[3].split()))

    ER = set()
    AR = set()
    arestas = {}
    arcos = {}

    i = 4
    while i < len(linhas):
        u, v, custo, demanda = map(int, linhas[i].split())

        if u == v:
            i += 1
            continue

        if (u, v) in arcos or (v, u) in arcos:
            chave = (u, v)
            arcos[chave] = {
                "custo": custo,
                "demanda": demanda,
                "requer_serviço": demanda > 0,
            }
            if demanda > 0:
                AR.add(chave)
        elif frozenset({u, v}) in arestas:
            chave = frozenset({u, v})
            arestas[chave]["custo"] = custo
            arestas[chave]["demanda"] = demanda
            arestas[chave]["requer_serviço"] = demanda > 0
            if demanda > 0:
                ER.add(chave)
        else:
            if i <= 4:
                chave = frozenset({u, v})
                arestas[chave] = {
                    "custo": custo,
                    "demanda": demanda,
                    "requer_serviço": demanda > 0,
                }
                if demanda > 0:
                    ER.add(chave)
            else:
                chave = (u, v)
                arcos[chave] = {
                    "custo": custo,
                    "demanda": demanda,
                    "requer_serviço": demanda > 0,
                }
                if demanda > 0:
                    AR.add(chave)
        i += 1

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


def visualizar_grafo(grafo):
    import matplotlib.patches as mpatches
    import matplotlib.lines as mlines

    G = nx.MultiDiGraph()

    for v in grafo["V"]:
        G.add_node(v)

    for e, dados in grafo["arestas"].items():
        u, v = list(e)
        cor = "red" if dados["requer_serviço"] else "gray"
        G.add_edge(u, v, custo=dados["custo"], demanda=dados["demanda"], color=cor)
        G.add_edge(v, u, custo=dados["custo"], demanda=dados["demanda"], color=cor)

    for (u, v), dados in grafo["arcos"].items():
        cor = "red" if dados["requer_serviço"] else "gray"
        G.add_edge(u, v, custo=dados["custo"], demanda=dados["demanda"], color=cor)

    pos = nx.spring_layout(G)
    plt.figure(figsize=(10, 7))

    deposito = grafo["deposito"]
    nos_com_servico = grafo["VR"]
    outros_nos = grafo["V"] - nos_com_servico - {deposito}

    # Desenhar depósito
    nx.draw_networkx_nodes(
        G, pos, nodelist=[deposito], node_color="orange", node_shape="s", node_size=800
    )

    # Desenhar nós com serviço
    nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=list(nos_com_servico),
        node_color="lightgreen",
        node_shape="o",
        node_size=700,
    )

    # Desenhar nós comuns
    nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=list(outros_nos),
        node_color="skyblue",
        node_shape="o",
        node_size=700,
    )

    # Rótulos dos nós
    nx.draw_networkx_labels(G, pos)

    # Desenhar arestas e arcos
    edge_colors = [d["color"] for _, _, d in G.edges(data=True)]
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, arrows=True, arrowstyle="->")

    # Rótulos das arestas
    edge_labels = {
        (u, v): f"c:{d['custo']} q:{d['demanda']}" for u, v, d in G.edges(data=True)
    }
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

    # === LEGENDA ===
    legenda_elementos = [
        mpatches.Patch(color="orange", label="Depósito (quadrado)"),
        mpatches.Patch(color="lightgreen", label="Nó com serviço"),
        mpatches.Patch(color="skyblue", label="Nó comum"),
        mlines.Line2D([], [], color="red", label="Aresta/arco com serviço"),
        mlines.Line2D([], [], color="gray", label="Aresta/arco sem serviço"),
    ]

    plt.legend(handles=legenda_elementos, loc="upper left")
    plt.title("Grafo com diferenciação de elementos e legenda")
    plt.axis("off")
    plt.tight_layout()
    plt.show()


# === Execução ===
grafo = ler_grafo_para_visualizacao("entrada.txt")
visualizar_grafo(grafo)
