import re
import os
import math
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import pandas as pd


class GrafoEtapa1:
    def __init__(self):
        self.nome = ""
        self.tipo = "CARP"
        self.numVertices = 0
        self.numArestas = 0
        self.numArcos = 0
        self.numArestasReq = 0
        self.numArcosReq = 0
        self.capacidade = 0
        self.custoTotal = 0
        self.deposito = None
        self.vertices = set()
        self.arestas = {}
        self.arcos = {}
        self.VR = set()
        self.ER = set()
        self.AR = set()
        self.adjMatrix = None
        self.matrizPredecessores = None
        self.matrizDistancias = None

    def inicializar_grafo(self, V, deposito, Q, edges, arcs, VR, ER, AR):
        self.vertices = V
        self.numVertices = max(V) if V else 0
        self.deposito = deposito
        self.capacidade = Q
        self.arestas = edges
        self.numArestas = len(edges)
        self.arcos = arcs
        self.numArcos = len(arcs)
        self.VR = VR
        self.ER = ER
        self.numArestasReq = len(ER)
        self.AR = AR
        self.numArcosReq = len(AR)
        self.custoTotal = sum(d["custo"] for d in edges.values()) + sum(
            d["custo"] for d in arcs.values()
        )
        self.inicializarMatrizAdjacencia()

    def inicializarMatrizAdjacencia(self):
        n = self.numVertices
        self.adjMatrix = [[float("inf")] * n for _ in range(n)]
        for i in range(n):
            self.adjMatrix[i][i] = 0
        for edge, data in self.arestas.items():
            u, v = tuple(edge)
            self.adjMatrix[u - 1][v - 1] = data["custo"]
            self.adjMatrix[v - 1][u - 1] = data["custo"]
        for (u, v), data in self.arcos.items():
            self.adjMatrix[u - 1][v - 1] = data["custo"]

    def adicionarAresta(self, u, v, custo, demanda, requerServico=False):
        edge = frozenset({u, v})
        self.arestas[edge] = {
            "custo": custo,
            "demanda": demanda,
            "requerServico": requerServico,
        }
        self.numArestas += 1
        self.adjMatrix[u - 1][v - 1] = custo
        self.adjMatrix[v - 1][u - 1] = custo
        if requerServico or demanda > 0:
            self.ER.add(edge)
            self.numArestasReq += 1
        self.custoTotal += custo

    def adicionarArco(self, u, v, custo, demanda, requerServico=False):
        arc = (u, v)
        self.arcos[arc] = {
            "custo": custo,
            "demanda": demanda,
            "requerServico": requerServico,
        }
        self.numArcos += 1
        self.adjMatrix[u - 1][v - 1] = custo
        if requerServico or demanda > 0:
            self.AR.add(arc)
            self.numArcosReq += 1
        self.custoTotal += custo

    def carregarDados(self, path):
        V, edges, arcs, VR, ER, AR = set(), {}, {}, set(), set(), set()
        deposito = capacidade = 0
        with open(path, "r") as file:
            section = None
            skip_header = False
            for line in file:
                line = line.strip()
                if not line or line.startswith("the data"):
                    continue
                
                # Processa variáveis via regex
                match = re.match(r"(.*?):\s*(\S+)", line)
                if match:
                    chave, valor = (
                        match.group(1).strip().upper().replace(" ", ""),
                        match.group(2).strip(),
                    )
                    if chave == "NAME":
                        self.nome = valor
                    elif chave == "CAPACITY":
                        capacidade = int(valor)
                    elif chave == "DEPOTNODE":
                        deposito = int(valor)
                    continue
                
                # Identifica seções
                if line.startswith("ReN."):
                    section = "NO_REQ"
                    skip_header = True  # Próxima linha é cabeçalho
                    continue
                if line.startswith("ReE."):
                    section = "ARESTA_REQ"
                    continue
                if line.startswith("ReA."):
                    section = "ARCO_REQ"
                    continue
                if line.startswith("ARC"):
                    section = "ARCO_NREQ"
                    continue
                if line.startswith("EDGE"):
                    section = "ARESTA_NREQ"
                    continue
                
                # Pula linha de cabeçalho após ReN.
                if skip_header and ("DEMAND" in line or "S. COST" in line):
                    skip_header = False
                    continue
                
                tokens = line.split()
                if not tokens:
                    continue
                
                # Remove prefixos não numéricos (como 'N')
                if not tokens[0][0].isdigit():
                    tokens[0] = tokens[0][1:] if tokens[0].startswith('N') else tokens[0]
                    if not tokens[0].isdigit():
                        tokens = tokens[1:]
                
                try:
                    if section == "NO_REQ":
                        if tokens[0].isdigit():
                            node = int(tokens[0])
                            if node != deposito:
                                VR.add(node)
                            V.add(node)
                    elif section == "ARESTA_REQ":
                        u, v, custo, demanda, _ = map(int, tokens)
                        edges[frozenset({u, v})] = {
                            "custo": custo,
                            "demanda": demanda,
                            "requerServico": True,
                        }
                        ER.add(frozenset({u, v}))
                        V.update([u, v])  # Adiciona aos nós totais, mas não a VR
                    elif section == "ARCO_REQ":
                        u, v, custo, demanda, _ = map(int, tokens)
                        arcs[(u, v)] = {
                            "custo": custo,
                            "demanda": demanda,
                            "requerServico": True,
                        }
                        AR.add((u, v))
                        V.update([u, v])  # Adiciona aos nós totais, mas não a VR
                    elif section == "ARESTA_NREQ":
                        u, v, custo = map(int, tokens)
                        edges[frozenset({u, v})] = {
                            "custo": custo,
                            "demanda": 0,
                            "requerServico": False,
                        }
                        V.update([u, v])
                    elif section == "ARCO_NREQ":
                        u, v, custo = map(int, tokens)
                        arcs[(u, v)] = {
                            "custo": custo,
                            "demanda": 0,
                            "requerServico": False,
                        }
                        V.update([u, v])
                except ValueError:
                    continue
        
        self.inicializar_grafo(V, deposito, capacidade, edges, arcs, VR, ER, AR)

    def calcularDistanciasMinimas(self):
        n = self.numVertices
        dist = [row[:] for row in self.adjMatrix]
        pred = [[None for _ in range(n)] for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i != j and dist[i][j] != float("inf"):
                    pred[i][j] = i
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if dist[i][j] > dist[i][k] + dist[k][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
                        pred[i][j] = pred[k][j]
        self.matrizDistancias = dist
        self.matrizPredecessores = pred
        return dist

    def obterDistanciaMinima(self, origem, destino):
        if not hasattr(self, "matrizDistancias") or self.matrizDistancias is None:
            self.calcularDistanciasMinimas()
        return self.matrizDistancias[origem - 1][destino - 1]

    def obterCaminhoMinimo(self, origem, destino):
        if not hasattr(self, "matrizPredecessores") or self.matrizPredecessores is None:
            self.calcularDistanciasMinimas()
        if self.matrizDistancias[origem - 1][destino - 1] == float("inf"):
            return None
        caminho = []
        no_atual = destino - 1
        while no_atual is not None:
            caminho.append(no_atual + 1)
            no_atual = self.matrizPredecessores[origem - 1][no_atual]
        caminho.reverse()
        return caminho if caminho and caminho[0] == origem else None

    def calcularDiametro(self):
        if not hasattr(self, "matrizDistancias") or self.matrizDistancias is None:
            self.calcularDistanciasMinimas()
        diametro = 0
        for i in range(self.numVertices):
            for j in range(i + 1, self.numVertices):
                if self.matrizDistancias[i][j] != float("inf"):
                    diametro = max(diametro, self.matrizDistancias[i][j])
        return diametro


def modelarGrafo(grafo):
    num_vertices = grafo.numVertices
    if num_vertices == 0:
        print("⚠️ Grafo vazio. Nenhum vértice encontrado.")
        return

    angulo = 2 * math.pi / max(1, num_vertices)
    posicoes = {
        i + 1: (math.cos(i * angulo), math.sin(i * angulo)) for i in range(num_vertices)
    }
    plt.figure(figsize=(10, 7))
    deposito = grafo.deposito
    nos_com_servico = grafo.VR
    outros_nos = grafo.vertices - nos_com_servico - {deposito}
    for v, (x, y) in posicoes.items():
        if v == deposito:
            cor, marcador = "orange", "s"
        elif v in nos_com_servico:
            cor, marcador = "black", "o"
        else:
            cor, marcador = "skyblue", "^"
        plt.plot(x, y, marker=marcador, markersize=10, color=cor)
        plt.text(x, y + 0.05, str(v), ha="center", fontsize=10)
    for e, dados in grafo.arestas.items():
        u, v = list(e)
        x1, y1 = posicoes[u]
        x2, y2 = posicoes[v]
        cor = "red" if dados.get("requerServico", False) else "gray"
        plt.plot([x1, x2], [y1, y2], color=cor, linewidth=2)
        xm, ym = (x1 + x2) / 2, (y1 + y2) / 2
        plt.text(xm, ym, str(dados["custo"]), color=cor, fontsize=8)
    for (u, v), dados in grafo.arcos.items():
        x1, y1 = posicoes[u]
        x2, y2 = posicoes[v]
        dx, dy = x2 - x1, y2 - y1
        cor = "red" if dados.get("requerServico", False) else "gray"
        plt.arrow(
            x1,
            y1,
            dx * 0.85,
            dy * 0.85,
            head_width=0.05,
            length_includes_head=True,
            color=cor,
        )
        xm, ym = x1 + dx * 0.5, y1 + dy * 0.5
        plt.text(xm, ym, str(dados["custo"]), color=cor, fontsize=8)
    plt.axis("off")
    legenda = [
        mpatches.Patch(color="orange", label="Depósito (quadrado)"),
        mpatches.Patch(color="black", label="Nó com serviço (círculo)"),
        mpatches.Patch(color="skyblue", label="Nó comum (triângulo)"),
        mlines.Line2D([], [], color="red", label="Aresta/arco com serviço"),
        mlines.Line2D([], [], color="gray", label="Aresta/arco sem serviço"),
    ]
    plt.legend(handles=legenda, loc="upper left")
    plt.title(f"Grafo - {grafo.nome}")
    plt.tight_layout()
    plt.show()


# === FUNÇÃO DE CÁLCULO DE ESTATÍSTICAS ===
def calcularEstatisticas(grafo):

    # define o vetor para guardar as estatisticas
    estatisticas = {}

    # veritces, arestas e arcos
    estatisticas["Vértices"] = grafo.numVertices
    estatisticas["Arestas"] = len(grafo.arestas)
    estatisticas["Arcos"] = len(grafo.arcos)

    # verticies arestas e arcos requeridos (VR, ER, AR)
    vertices_requeridos = set()
    for u, v in grafo.arestas:
        vertices_requeridos.add(u)
        vertices_requeridos.add(v)
    for u, v in grafo.arcos:
        vertices_requeridos.add(u)
        vertices_requeridos.add(v)
    estatisticas["Vértices Requeridos"] = len(vertices_requeridos)
    estatisticas["Arestas Requeridas"] = sum(
        1 for e in grafo.arestas if grafo.arestas[e]["demanda"] > 0
    )
    estatisticas["Arcos Requeridos"] = sum(
        1 for a in grafo.arcos if grafo.arcos[a]["demanda"] > 0
    )

    num_arestas = estatisticas["Arestas"]
    num_arcos = estatisticas["Arcos"]
    num_vertices = estatisticas["Vértices"]

    # Calcula densidade
    if num_vertices > 1:
        if grafo.arcos and num_arestas > 0:
            max_nd = num_vertices * (num_vertices - 1) / 2  
            max_d = num_vertices * (num_vertices - 1)       
            max_misto = max_nd + max_d                     
            densidade = (num_arestas + num_arcos) / max_misto
        elif grafo.arcos:
            densidade = num_arcos / (num_vertices * (num_vertices - 1))
        else:
            densidade = 2 * num_arestas / (num_vertices * (num_vertices - 1))
    else:
        densidade = 0
    estatisticas["Densidade"] = densidade

    # calcula graus
    graus = {}
    for u, v in grafo.arestas:
        graus[u] = graus.get(u, 0) + 1
        graus[v] = graus.get(v, 0) + 1
    for u, v in grafo.arcos:
        graus[u] = graus.get(u, 0) + 1

    estatisticas["Grau Mínimo"] = min(graus.values()) if graus else 0
    estatisticas["Grau Máximo"] = max(graus.values()) if graus else 0

    # calcula intermediação
    intermediacao = {v: 0 for v in grafo.vertices}
    for u in grafo.vertices:
        for v in grafo.vertices:
            if u != v:
                caminho = grafo.obterCaminhoMinimo(u, v)
                if caminho:
                    for node in caminho[1:-1]:
                        intermediacao[node] += 1
    estatisticas["Intermediação"] = sum(intermediacao.values())

    # Caminho médio
    soma_distancias = 0
    total_pares = 0
    for u in grafo.vertices:
        for v in grafo.vertices:
            if u != v:
                dist = grafo.obterDistanciaMinima(u, v)
                if dist != float("inf"):
                    soma_distancias += dist
                    total_pares += 1
    estatisticas["Caminho Médio"] = (
        soma_distancias / total_pares if total_pares > 0 else 0
    )

    # calcula
    estatisticas["Diâmetro"] = grafo.calcularDiametro()
    return estatisticas
