import re  # Importa o módulo de expressões regulares, usado para processar strings ao carregar arquivos.
import math  # Importa funções matemáticas (nesse código, math não está sendo usado).


# Definição da classe principal para manipulação do grafo
class GrafoEtapa1:
    def __init__(self):
        # Inicializa todos os atributos do grafo com valores padrão
        self.nome = ""  # Nome do grafo (pode vir do arquivo de dados)
        self.tipo = "CARP"  # Tipo do grafo, fixo como 'CARP'
        self.numVertices = 0  # Número de vértices
        self.numArestas = 0  # Número total de arestas
        self.numArcos = 0  # Número total de arcos (direcionados)
        self.numArestasReq = 0  # Número de arestas que requerem serviço
        self.numArcosReq = 0  # Número de arcos que requerem serviço
        self.capacidade = 0  # Capacidade dos veículos (se aplicável)
        self.custoTotal = 0  # Soma dos custos das arestas e arcos
        self.deposito = None  # Nó depósito (inicial ou central)
        self.vertices = set()  # Conjunto de todos os vértices
        self.arestas = {}  # Dicionário de arestas (chave: frozenset dos nós)
        self.arcos = {}  # Dicionário de arcos (chave: tupla dos nós, direção importa)
        self.VR = set()  # Vértices que requerem serviço
        self.ER = set()  # Arestas que requerem serviço
        self.AR = set()  # Arcos que requerem serviço
        self.demanda_nos = {}  # Demanda específica de cada nó
        self.adjMatrix = None  # Matriz de adjacência (para distâncias)
        self.matrizPredecessores = (
            None  # Matriz de predecessores (para caminhos mínimos)
        )
        self.matrizDistancias = None  # Matriz de distâncias mínimas entre pares de nós

    # Função para inicializar o grafo após carregar os dados
    def inicializar_grafo(self, V, deposito, Q, edges, arcs, VR, ER, AR):
        self.vertices = V
        self.numVertices = (
            max(V) if V else 0
        )  # Assume que os vértices vão de 1 até o maior valor em V
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
        # Soma todos os custos de arestas e arcos para calcular o custo total inicial do grafo
        self.custoTotal = sum(d["custo"] for d in edges.values()) + sum(
            d["custo"] for d in arcs.values()
        )
        self._inicializarMatrizAdjacencia()  # Monta a matriz de adjacência

    # Método privado para criar a matriz de adjacência (usada nos cálculos de caminhos mínimos)
    def _inicializarMatrizAdjacencia(self):
        n = self.numVertices
        # Cria matriz n x n, inicializada com infinito (distância máxima possível)
        self.adjMatrix = [[float("inf")] * n for _ in range(n)]
        for i in range(n):
            self.adjMatrix[i][i] = 0  # Distância de um nó para ele mesmo é zero
        # Preenche matriz com os custos das arestas (grafo não direcionado)
        for edge, data in self.arestas.items():
            u, v = tuple(edge)
            self.adjMatrix[u - 1][v - 1] = data["custo"]
            self.adjMatrix[v - 1][u - 1] = data["custo"]
        # Preenche matriz com custos dos arcos (direcionados)
        for (u, v), data in self.arcos.items():
            self.adjMatrix[u - 1][v - 1] = data["custo"]

    # Adiciona uma nova aresta ao grafo, incluindo na matriz e atualizando contadores e sets
    def adicionarAresta(self, u, v, custo, demanda, requerServico=False):
        edge = frozenset({u, v})  # frozenset para arestas não direcionadas
        self.arestas[edge] = {
            "custo": custo,
            "demanda": demanda,
            "requerServico": requerServico,
        }
        self.numArestas += 1
        self.adjMatrix[u - 1][v - 1] = custo
        self.adjMatrix[v - 1][u - 1] = custo
        # Se precisa de serviço, adiciona a ER e aumenta o contador
        if requerServico or demanda > 0:
            self.ER.add(edge)
            self.numArestasReq += 1
        self.custoTotal += custo

    # Adiciona um arco (aresta direcionada)
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

    # Carrega os dados do grafo a partir de um arquivo
    def carregarDados(self, path):
        # Inicializa estruturas temporárias para armazenar dados durante a leitura
        V, edges, arcs, VR, ER, AR = set(), {}, {}, set(), set(), set()
        deposito = capacidade = 0
        demanda_nos_temp = {}  # Armazena as demandas dos nós lidas do arquivo
        with open(path, "r") as file:
            section = None  # Indica qual seção do arquivo está sendo lida
            skip_header = False  # Usado para pular linhas de cabeçalho nas seções
            for line in file:
                line = line.strip()
                if not line or line.startswith("the data"):
                    continue  # Pula linhas em branco ou cabeçalhos

                # Expressão regular para capturar variáveis globais no arquivo
                match = re.match(r"(.*?):\s*(\S+)", line)
                if match:
                    chave, valor = (
                        match.group(1).strip().upper().replace(" ", ""),
                        match.group(2).strip(),
                    )
                    # Interpreta as variáveis do cabeçalho do arquivo
                    if chave == "NAME":
                        self.nome = valor
                    elif chave == "CAPACITY":
                        capacidade = int(valor)
                    elif chave == "DEPOTNODE":
                        deposito = int(valor)
                    continue

                # Identifica mudança de seção no arquivo, conforme o prefixo da linha
                if line.startswith("ReN."):
                    section = "NO_REQ"
                    skip_header = True  # A próxima linha é um cabeçalho
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

                # Pula cabeçalho de coluna (ex: "NODE DEMAND ...") logo após 'ReN.'
                if skip_header and ("DEMAND" in line or "S. COST" in line):
                    skip_header = False
                    continue

                tokens = line.split()
                if not tokens:
                    continue

                # Remove possíveis prefixos não numéricos dos tokens (ex: 'N1' vira '1')
                if not tokens[0][0].isdigit():
                    tokens[0] = (
                        tokens[0][1:] if tokens[0].startswith("N") else tokens[0]
                    )
                    if not tokens[0].isdigit():
                        tokens = tokens[1:]

                try:
                    # Processa cada seção separadamente, criando as estruturas corretas
                    if section == "NO_REQ":
                        if tokens[0].isdigit():
                            node = int(tokens[0])
                            demanda = int(tokens[1])  # Demanda daquele nó
                            demanda_nos_temp[node] = demanda  # Salva demanda
                            if node != deposito:
                                VR.add(node)  # Nó requer serviço se não for depósito
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
                    continue  # Pula linhas que não correspondem ao formato esperado
        self.demanda_nos = (
            demanda_nos_temp  # Salva as demandas dos nós no atributo do objeto
        )
        # Inicializa o grafo já com todos os dados processados
        self.inicializar_grafo(V, deposito, capacidade, edges, arcs, VR, ER, AR)

    # Calcula as menores distâncias entre todos os pares de vértices (Floyd-Warshall)
    def calcularDistanciasMinimas(self):
        n = self.numVertices
        dist = [row[:] for row in self.adjMatrix]  # Cria cópia da matriz de adjacência
        pred = [[None for _ in range(n)] for _ in range(n)]  # Matriz de predecessores
        for i in range(n):
            for j in range(n):
                if i != j and dist[i][j] != float("inf"):
                    pred[i][j] = i  # O predecessor inicial de j, vindo de i, é i
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if dist[i][j] > dist[i][k] + dist[k][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
                        pred[i][j] = pred[k][
                            j
                        ]  # Atualiza predecessor se encontrou caminho mais curto
        self.matrizDistancias = dist
        self.matrizPredecessores = pred
        return dist

    # Retorna a menor distância entre dois nós (origem, destino)
    def obterDistanciaMinima(self, origem, destino):
        if not hasattr(self, "matrizDistancias") or self.matrizDistancias is None:
            self.calcularDistanciasMinimas()
        return self.matrizDistancias[origem - 1][destino - 1]

    # Retorna o caminho mínimo (lista de nós) entre dois nós
    def obterCaminhoMinimo(self, origem, destino):
        if not hasattr(self, "matrizPredecessores") or self.matrizPredecessores is None:
            self.calcularDistanciasMinimas()
        if self.matrizDistancias[origem - 1][destino - 1] == float("inf"):
            return None  # Não existe caminho entre os nós
        caminho = []
        no_atual = destino - 1
        while no_atual is not None:
            caminho.append(no_atual + 1)  # Adiciona nó ao caminho (ajusta para base 1)
            no_atual = self.matrizPredecessores[origem - 1][no_atual]
        caminho.reverse()
        return (
            caminho if caminho and caminho[0] == origem else None
        )  # Garante que começa no nó de origem
