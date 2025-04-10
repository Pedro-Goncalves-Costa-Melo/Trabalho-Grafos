import re
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
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
        self.adjMatrix = None
        self.matrizPredecessores = None

    def inicializarGrafo(self, V, deposito, Q, edges, arcs, VR, ER, AR):
        self.vertices = V
        self.numVertices = len(V)
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

        self.custoTotal = sum(data["custo"] for data in edges.values()) + sum(
            data["custo"] for data in arcs.values()
        )

        self.inicializarMatrizAdjacencia()

    def inicializarMatrizAdjacencia(self):
        n = self.numVertices
        self.adjMatrix = [[float("inf")] * n for _ in range(n)]

        # Diagonal principal
        for i in range(n):
            self.adjMatrix[i][i] = 0

        # Preencher com arestas (bidirecional)
        for edge, data in self.arestas.items():
            u, v = tuple(edge)
            self.adjMatrix[u][v] = data["custo"]
            self.adjMatrix[v][u] = data["custo"]

        # Preencher com arcos (unidirecional)
        for (u, v), data in self.arcos.items():
            self.adjMatrix[u][v] = data["custo"]

    def adicionarAresta(self, u, v, custo, demanda, requerServico=False):
        edge = frozenset({u, v})
        self.arestas[edge] = {
            "custo": custo,
            "demanda": demanda,
            "requerServico": requerServico,
        }
        self.numArestas += 1

        # Atualizar matriz de adjacência
        self.adjMatrix[u][v] = custo
        self.adjMatrix[v][u] = custo

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

        # Atualizar matriz de adjacência
        self.adjMatrix[u][v] = custo

        if requerServico or demanda > 0:
            self.AR.add(arc)
            self.numArcosReq += 1

        self.custoTotal += custo


def carregarDados(self, path):
    V = set()
    edges = {}
    arcs = {}
    VR = set()
    ER = set()
    AR = set()
    deposito = None
    capacidade = 0

    with open(path, "r") as file:
        section = None
        for line in file:
            line = line.strip()

            # Ignorar linhas em branco ou com o cabeçalho
            if not line or line.startswith("the data"):
                continue

            match = re.match(r"(.*?):\s*(\S+)", line)
            if match:
                chave = match.group(1).strip().upper().replace("#", "").replace(" ", "")
                valor = match.group(2).strip()

                # Definir os parâmetros principais
                if chave == "NAME":
                    self.nome = valor
                elif chave == "CAPACITY":
                    capacidade = int(valor)
                elif chave == "DEPOTNODE":
                    deposito = int(valor)
                elif chave == "NODES":
                    num_vertices = int(valor)
                elif chave == "EDGES":
                    self.num_arestas = int(valor)
                elif chave == "ARCS":
                    self.num_arcos = int(valor)
                elif chave == "REQUIREDE":
                    self.num_arestas_req = int(valor)
                elif chave == "REQUIREDA":
                    self.num_arcos_req = int(valor)

                continue

            # Seções de leitura de dados
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

            if section == "ARESTA_REQ":
                u, v, custo, demanda, _ = map(int, line.split())
                edges[(u, v)] = {"custo": custo, "demanda": demanda}
                ER.add((u, v))

            elif section == "ARCO_REQ":
                u, v, custo, demanda, _ = map(int, line.split())
                arcs[(u, v)] = {"custo": custo, "demanda": demanda}
                AR.add((u, v))

            elif section == "ARESTA_NREQ":
                u, v, custo = map(int, line.split())
                edges[(u, v)] = {"custo": custo, "demanda": 0}
                VR.add(u)
                VR.add(v)

            elif section == "ARCO_NREQ":
                u, v, custo = map(int, line.split())
                arcs[(u, v)] = {"custo": custo, "demanda": 0}
                VR.add(u)
                VR.add(v)

    self.inicializar_grafo(VR, deposito, capacidade, edges, arcs, VR, ER, AR)


def modelarGrafo(grafo):
    num_vertices = grafo.numVertices
    angulo = 2 * math.pi / num_vertices
    posicoes = {
        i + 1: (math.cos(i * angulo), math.sin(i * angulo)) for i in range(num_vertices)
    }

    # Criar a figura para o gráfico
    plt.figure(figsize=(10, 7))

    # Desenhar depósito (quadrado laranja)
    deposito = grafo.deposito
    nos_com_servico = grafo.VR
    outros_nos = grafo.vertices - nos_com_servico - {deposito}

    # Desenhar os nós
    for v, (x, y) in posicoes.items():
        if v == deposito:
            cor = "orange"
            marcador = "s"  # quadrado para o depósito
        elif v in nos_com_servico:
            cor = "lightgreen"
            marcador = "o"  # círculo para nós com serviço
        else:
            cor = "skyblue"
            marcador = "^"  # triângulo para nós comuns

        plt.plot(x, y, marker=marcador, markersize=10, color=cor)
        plt.text(x, y + 0.05, str(v), ha="center", fontsize=10)

    # Desenhar as arestas (bidirecionais)
    for e, dados in grafo.arestas.items():
        u, v = list(e)
        x1, y1 = posicoes[u]
        x2, y2 = posicoes[v]
        cor = "red" if dados["requerServico"] else "gray"
        plt.plot([x1, x2], [y1, y2], color=cor, linewidth=2)
        xm, ym = (x1 + x2) / 2, (y1 + y2) / 2
        plt.text(xm, ym, str(dados["custo"]), color=cor, fontsize=8)

    # Desenhar os arcos (unidirecionais)
    for (u, v), dados in grafo.arcos.items():
        x1, y1 = posicoes[u]
        x2, y2 = posicoes[v]
        dx, dy = x2 - x1, y2 - y1
        cor = "red" if dados["requerServico"] else "gray"
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

    # Rótulos dos nós
    plt.axis("off")

    # === LEGENDA ===
    legenda_elementos = [
        mpatches.Patch(color="orange", label="Depósito (quadrado)"),
        mpatches.Patch(color="lightgreen", label="Nó com serviço (círculo)"),
        mpatches.Patch(color="skyblue", label="Nó comum (triângulo)"),
        mlines.Line2D([], [], color="red", label="Aresta/arco com serviço"),
        mlines.Line2D([], [], color="gray", label="Aresta/arco sem serviço"),
    ]

    plt.legend(handles=legenda_elementos, loc="upper left")
    plt.title("Visualização do Grafo com Diferenciação de Elementos")
    plt.tight_layout()
    plt.show()


def calcularDistanciasMinimas(self):
    n = self.numVertices
    dist = [row[:] for row in self.adjMatrix]  # Cópia da matriz de adjacência
    pred = [[None for _ in range(n)] for _ in range(n)]  # Matriz de predecessores

    # Inicialização da matriz de predecessores
    for i in range(n):
        for j in range(n):
            if i != j and dist[i][j] != float("inf"):
                pred[i][j] = i

    # Algoritmo Floyd-Warshall
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][j] > dist[i][k] + dist[k][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    pred[i][j] = pred[k][j]  # Atualiza o predecessor

    # Armazena as matrizes como atributos do objeto
    self.matrizDistancias = dist
    self.matrizPredecessores = pred
    return dist


def obterDistanciaMinima(self, origem, destino):
    if not hasattr(self, "matrizDistancias"):
        self.calcularDistanciasMinimas()
    return self.matrizDistancias[origem][destino]


def obterCaminhoMinimo(self, origem, destino):
    if not hasattr(self, "matrizPredecessores"):
        self.calcularDistanciasMinimas()

    if self.matrizDistancias[origem][destino] == float("inf"):
        return None

    caminho = []
    no_atual = destino

    # Reconstrução do caminho do destino até a origem
    while no_atual is not None:
        caminho.append(no_atual)
        no_atual = self.matrizPredecessores[origem][no_atual]

    # Inverte o caminho para ficar origem->destino
    caminho.reverse()

    # Verifica se o caminho começa na origem correta
    return caminho if caminho and caminho[0] == origem else None


def calcularDiametro(self):
    if not hasattr(self, "matrizDistancias"):
        self.calcularDistanciasMinimas()

    diametro = 0
    for i in range(self.numVertices):
        for j in range(i + 1, self.numVertices):
            if self.matrizDistancias[i][j] != float("inf"):
                diametro = max(diametro, self.matrizDistancias[i][j])

    return diametro


def calcularEstatisticas(grafo):
    estatisticas = {}

    # 1. Contagem de vértices
    estatisticas["Vértices"] = grafo.num_vertices

    # 2. Contagem de arestas
    estatisticas["Arestas"] = sum(1 for _ in grafo.arestas)

    # 3. Contagem de arcos
    estatisticas["Arcos"] = sum(1 for _ in grafo.arcos)

    # 4. Quantidade de vértices requeridos
    vertices_requeridos = set()
    for u, v in grafo.arestas:
        vertices_requeridos.add(u)
        vertices_requeridos.add(v)
    for u, v in grafo.arcos:
        vertices_requeridos.add(u)
        vertices_requeridos.add(v)
    estatisticas["Vértices Requeridos"] = len(vertices_requeridos)

    # 5. Quantidade de arestas requeridas
    estatisticas["Arestas Requeridas"] = sum(
        1 for e in grafo.arestas if grafo.arestas[e]["demanda"] > 0
    )

    # 6. Quantidade de arcos requeridos
    estatisticas["Arcos Requeridos"] = sum(
        1 for a in grafo.arcos if grafo.arcos[a]["demanda"] > 0
    )

    # 7. Densidade do grafo
    num_arestas = estatisticas["Arestas"]
    num_arcos = estatisticas["Arcos"]
    num_vertices = estatisticas["Vértices"]
    if grafo.arcos:  # Se houver arcos, é um grafo direcionado
        densidade = (num_arestas + num_arcos) / (num_vertices * (num_vertices - 1))
    else:  # Grafo não direcionado
        densidade = 2 * (num_arestas + num_arcos) / (num_vertices * (num_vertices - 1))
    estatisticas["Densidade"] = densidade

    # 8. Grau mínimo e máximo dos vértices
    graus = {}
    for u, v in grafo.arestas:
        graus[u] = graus.get(u, 0) + 1
        graus[v] = graus.get(v, 0) + 1
    for u, v in grafo.arcos:
        graus[u] = graus.get(u, 0) + 1
        graus[v] = graus.get(v, 0) + 1

    grau_minimo = min(graus.values())
    grau_maximo = max(graus.values())
    estatisticas["Grau Mínimo"] = grau_minimo
    estatisticas["Grau Máximo"] = grau_maximo

    # 9. Intermediação - Centralidade de Intermediação (simplificada)
    intermediacao = {v: 0 for v in grafo.vertices}
    for u in grafo.vertices:
        for v in grafo.vertices:
            if u != v:
                caminho = grafo.obterCaminhoMinimo(u, v)
                if caminho:
                    for node in caminho[1:-1]:  # Nós intermediários
                        intermediacao[node] += 1
    estatisticas["Intermediação"] = intermediacao

    # 10. Caminho médio
    soma_distancias = 0
    total_pares = 0
    for u in grafo.vertices:
        for v in grafo.vertices:
            if u != v:
                dist = grafo.obterDistanciaMinima(u, v)
                if dist != float("inf"):
                    soma_distancias += dist
                    total_pares += 1
    if total_pares > 0:
        caminho_medio = soma_distancias / total_pares
    else:
        caminho_medio = 0
    estatisticas["Caminho Médio"] = caminho_medio

    # 11. Diâmetro - Maior distância entre dois vértices
    diamentro = 0
    for u in grafo.vertices:
        for v in grafo.vertices:
            if u != v:
                dist = grafo.obterDistanciaMinima(u, v)
                if dist != float("inf"):
                    diamentro = max(diamentro, dist)
    estatisticas["Diâmetro"] = diamentro

    return estatisticas
