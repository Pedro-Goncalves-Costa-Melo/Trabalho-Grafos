import re
import os
import math
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines

# === CLASSE GRAFO COM TODAS AS FUNÇÕES AJUSTADAS ===
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
        self.numVertices = max(V)  # Assume vértices numerados de 1 a N
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
        self.custoTotal = sum(d["custo"] for d in edges.values()) + sum(d["custo"] for d in arcs.values())
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
            for line in file:
                line = line.strip()
                if not line or line.startswith("the data"): continue
                match = re.match(r"(.*?):\s*(\S+)", line)
                if match:
                    chave, valor = match.group(1).strip().upper(), match.group(2).strip()
                    if chave == "NAME": self.nome = valor
                    elif chave == "CAPACITY": capacidade = int(valor)
                    elif chave == "DEPOTNODE": deposito = int(valor)
                    continue
                if line.startswith("ReE."): section = "ARESTA_REQ"; continue
                if line.startswith("ReA."): section = "ARCO_REQ"; continue
                if line.startswith("ARC"): section = "ARCO_NREQ"; continue
                if line.startswith("EDGE"): section = "ARESTA_NREQ"; continue
                tokens = line.split()
                if not tokens: continue
                if not tokens[0].isdigit(): tokens = tokens[1:]

                # Verificar se os dois primeiros tokens são números válidos
                try:
                    if section == "ARESTA_REQ":
                        u, v, custo, demanda, _ = map(int, tokens)
                        edges[frozenset({u, v})] = {"custo": custo, "demanda": demanda, "requerServico": True}
                        ER.add(frozenset({u, v}))
                        VR.update([u, v])
                    elif section == "ARCO_REQ":
                        u, v, custo, demanda, _ = map(int, tokens)
                        arcs[(u, v)] = {"custo": custo, "demanda": demanda, "requerServico": True}
                        AR.add((u, v))
                        VR.update([u, v])
                    elif section == "ARESTA_NREQ":
                        u, v, custo = map(int, tokens)
                        edges[frozenset({u, v})] = {"custo": custo, "demanda": 0, "requerServico": False}
                        VR.update([u, v])
                    elif section == "ARCO_NREQ":
                        u, v, custo = map(int, tokens)
                        arcs[(u, v)] = {"custo": custo, "demanda": 0, "requerServico": False}
                        VR.update([u, v])
                except ValueError:
                  continue  # pula linhas inválidas sem quebrar
        self.inicializar_grafo(VR, deposito, capacidade, edges, arcs, VR, ER, AR)

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