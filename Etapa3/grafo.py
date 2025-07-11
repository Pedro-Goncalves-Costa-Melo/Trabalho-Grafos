import re
import math


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
        self.demanda_nos = {}  # Adicionado para armazenar a demanda dos nós
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
        self._inicializarMatrizAdjacencia()  # Chamada corrigida

    def _inicializarMatrizAdjacencia(self):  # Renomeado para método privado
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
        demanda_nos_temp = {}  # Dicionário temporário para armazenar demandas dos nós
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

                # Remove prefixos não numéricos (como \'N\')
                if not tokens[0][0].isdigit():
                    tokens[0] = (
                        tokens[0][1:] if tokens[0].startswith("N") else tokens[0]
                    )
                    if not tokens[0].isdigit():
                        tokens = tokens[1:]

                try:
                    if section == "NO_REQ":
                        if tokens[0].isdigit():
                            node = int(tokens[0])
                            demanda = int(tokens[1])  # Captura a demanda do nó
                            demanda_nos_temp[node] = demanda  # Armazena a demanda
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
                        V.update([u, v])
                    elif section == "ARCO_REQ":
                        u, v, custo, demanda, _ = map(int, tokens)
                        arcs[(u, v)] = {
                            "custo": custo,
                            "demanda": demanda,
                            "requerServico": True,
                        }
                        AR.add((u, v))
                        V.update([u, v])
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
        self.demanda_nos = demanda_nos_temp  # Atribui o dicionário de demandas dos nós
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
