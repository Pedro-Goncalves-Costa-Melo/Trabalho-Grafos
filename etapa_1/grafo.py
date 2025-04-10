import re
import matplotlib.pyplot as plt
import math


class Grafo:
    def __init__(self, num_vertices):
        self.nome = ""
        self.tipo = "CARP"
        self.num_vertices = num_vertices
        self.num_arestas = 0
        self.num_arcos = 0
        self.num_arestas_req = 0
        self.num_arcos_req = 0
        self.capacidade = 0
        self.custo_total = 0
        self.deposito = None
        self.arestas = []
        self.arcos = []
        self.arestas_req = []
        self.arcos_req = []
        self.adj_matrix = [
            [float('inf')] * num_vertices for _ in range(num_vertices)
        ]
        for i in range(num_vertices):
            self.adj_matrix[i][i] = 0


    def adicionar_aresta(self, u, v, custo, demanda):
        self.arestas.append((u, v, custo, demanda))
        if demanda > 0:
            self.arestas_req.append((u, v, custo, demanda))
        self.adj_matrix[u-1][v-1] = custo
        self.adj_matrix[v-1][u-1] = custo


    def adicionar_arco(self, u, v, custo, demanda):
        self.arcos.append((u, v, custo, demanda))
        if demanda > 0:
            self.arcos_req.append((u, v, custo, demanda))
        self.adj_matrix[u-1][v-1] = custo


def ler_arquivo(path):
    grafo = None
    secao = None
    nome = ""
    capacidade = 0
    deposito = None
    num_vertices = None


    with open(path, 'r') as f:
        for linha in f:
            linha = linha.strip()
            if not linha or linha.startswith("the data"):
                continue

            
            match = re.match(r"(.*?):\s*(\S+)", linha)
            if match:
                chave = match.group(1).strip().upper().replace('#', '').replace(' ', '')
                valor = match.group(2).strip()


                if chave == "NAME":
                    nome = valor
                elif chave == "CAPACITY":
                    capacidade = int(valor)
                elif chave == "DEPOTNODE":
                    deposito = int(valor)
                elif chave == "NODES":
                    num_vertices = int(valor)
                    grafo = Grafo(num_vertices)
                elif chave == "EDGES" and grafo:
                    grafo.num_arestas = int(valor)
                elif chave == "ARCS" and grafo:
                    grafo.num_arcos = int(valor)
                elif chave == "REQUIREDE" and grafo:
                    grafo.num_arestas_req = int(valor)
                elif chave == "REQUIREDA" and grafo:
                    grafo.num_arcos_req = int(valor)

                
                if grafo:
                    grafo.nome = nome
                    grafo.capacidade = capacidade
                    grafo.deposito = deposito


                continue

            
            if linha.startswith("ReE."):
                secao = "ARESTA_REQ"
                continue
            if linha.startswith("ReA."):
                secao = "ARCO_REQ"
                continue
            if linha.startswith("ARC"):
                secao = "ARCO_NREQ"
                continue
            if linha.startswith("EDGE"):
                secao = "ARESTA_NREQ"
                continue

            
            if grafo:
                partes = linha.split()
                if secao == "ARESTA_REQ" and len(partes) >= 6:
                    _, u, v, custo, demanda, _ = partes
                    grafo.adicionar_aresta(int(u), int(v), int(custo), int(demanda))
                elif secao == "ARCO_REQ" and len(partes) >= 6:
                    _, u, v, custo, demanda, _ = partes
                    grafo.adicionar_arco(int(u), int(v), int(custo), int(demanda))
                elif secao == "ARESTA_NREQ" and len(partes) >= 4:
                    _, u, v, custo = partes
                    grafo.adicionar_aresta(int(u), int(v), int(custo), 0)
                elif secao == "ARCO_NREQ" and len(partes) >= 4:
                    if not linha.strip():
                        break 
                    if len(partes) >= 4 and partes[-3].isdigit() and partes[-2].isdigit() and partes[-1].isdigit():
                        _, u, v, custo = partes[-4:]
                        grafo.adicionar_arco(int(u), int(v), int(custo), 0)
                    else:
                        break


    return grafo


def desenhar_grafo(grafo):
    num_vertices = grafo.num_vertices
    angulo = 2 * math.pi / num_vertices

    
    posicoes = {
        i + 1: (
            math.cos(i * angulo),
            math.sin(i * angulo)
        )
        for i in range(num_vertices)
    }


    fig, ax = plt.subplots(figsize=(8, 8))

    
    for v, (x, y) in posicoes.items():
        cor = 'purple' if v == grafo.deposito else 'skyblue'
        ax.plot(x, y, 'o', markersize=10, color=cor)
        ax.text(x, y + 0.05, str(v), ha='center', fontsize=10)

    
    for u, v, custo, _ in grafo.arestas:
        x1, y1 = posicoes[u]
        x2, y2 = posicoes[v]
        ax.plot([x1, x2], [y1, y2], 'k-', linewidth=1)
        xm, ym = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(xm, ym, str(custo), color='blue', fontsize=8)

    
    for u, v, custo, _ in grafo.arcos:
        x1, y1 = posicoes[u]
        x2, y2 = posicoes[v]
        dx, dy = x2 - x1, y2 - y1
        ax.arrow(x1, y1, dx * 0.85, dy * 0.85,
                 head_width=0.05, length_includes_head=True, color='red')
        xm, ym = x1 + dx * 0.5, y1 + dy * 0.5
        ax.text(xm, ym, str(custo), color='red', fontsize=8)


    ax.set_aspect('equal')
    ax.axis('off')
    plt.title(f"Grafo: {grafo.nome}")
    plt.show()


def floyd_warshall(grafo):
    n = grafo.num_vertices
    dist = [[float('inf')] * n for _ in range(n)]
    pred = [[None] * n for _ in range(n)]


    for i in range(n):
        dist[i][i] = 0


    for u in range(n):
        for v in range(n):
            if grafo.adj_matrix[u][v] != float('inf'):
                dist[u][v] = grafo.adj_matrix[u][v]
                pred[u][v] = u


    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    pred[i][j] = pred[k][j]


    return dist, pred


def reconstruir_caminho(pred, s, t):
    caminho = []
    if pred[s][t] is None:
        return caminho
    while t != s:
        caminho.insert(0, t)
        t = pred[s][t]
    caminho.insert(0, s)
    return caminho


def calcular_intermediacao_fw(grafo):
    n = grafo.num_vertices
    dist, pred = floyd_warshall(grafo)
    intermediacao = {v: 0 for v in range(1, n + 1)}


    for s in range(n):
        for t in range(n):
            if s != t:
                caminho = reconstruir_caminho(pred, s, t)
                for v in caminho[1:-1]:  
                    intermediacao[v + 1] += 1 


    return intermediacao


def calcular_caminho_medio(grafo):
    dist, _ = floyd_warshall(grafo)
    n = grafo.num_vertices
    soma = 0
    total_pares = 0


    for i in range(n):
        for j in range(n):
            if i != j and dist[i][j] != float('inf'):
                soma += dist[i][j]
                total_pares += 1


    caminho_medio = soma / total_pares if total_pares > 0 else 0
    return round(caminho_medio, 3)


def calcular_diametro(grafo):
    dist, _ = floyd_warshall(grafo)
    n = grafo.num_vertices
    diametro = 0


    for i in range(n):
        for j in range(n):
            if i != j and dist[i][j] != float('inf'):
                diametro = max(diametro, dist[i][j])


    return diametro


def estatisticas_grafo(grafo):
    # 1. 
    qtd_vertices = grafo.num_vertices

    # 2. 
    qtd_arestas = len(grafo.arestas)

    # 3. 
    qtd_arcos = len(grafo.arcos)

    # 4. 
    vertices_requeridos = set()
    for u, v, _, _ in grafo.arestas_req:
        vertices_requeridos.add(u)
        vertices_requeridos.add(v)
    for u, v, _, _ in grafo.arcos_req:
        vertices_requeridos.add(u)
        vertices_requeridos.add(v)
    qtd_vertices_requeridos = len(vertices_requeridos)

    # 5. 
    qtd_arestas_req = len(grafo.arestas_req)

    # 6. 
    qtd_arcos_req = len(grafo.arcos_req)

    # 7. 
    n = qtd_vertices
    m = qtd_arestas + qtd_arcos
    if grafo.arcos:  # se há arcos, considera como direcionado
        densidade = m / (n * (n - 1)) if n > 1 else 0
    else:
        densidade = 2 * m / (n * (n - 1)) if n > 1 else 0

    # 9 e 10. 
    grau_in = {v: 0 for v in range(1, n + 1)}
    grau_out = {v: 0 for v in range(1, n + 1)}
    for u, v, *_ in grafo.arestas:
        grau_in[u] += 1
        grau_out[u] += 1
        grau_in[v] += 1
        grau_out[v] += 1
    for u, v, *_ in grafo.arcos:
        grau_out[u] += 1
        grau_in[v] += 1

    grau_total = {v: grau_in[v] + grau_out[v] for v in grau_in}
    grau_min = min(grau_total.values())
    grau_max = max(grau_total.values())

    # 11. 
    intermediacao = calcular_intermediacao_fw(grafo)

    # 12. 
    caminho_medio = calcular_caminho_medio(grafo)

    # 13. 
    diametro = calcular_diametro(grafo)


    return {
        "Qtd Vértices": qtd_vertices,
        "Qtd Arestas": qtd_arestas,
        "Qtd Arcos": qtd_arcos,
        "Qtd Vértices Requeridos": qtd_vertices_requeridos,
        "Qtd Arestas Requeridas": qtd_arestas_req,
        "Qtd Arcos Requeridos": qtd_arcos_req,
        "Densidade": densidade,
        "Grau Mínimo": grau_min,
        "Grau Máximo": grau_max,
        "Intermediação": intermediacao,
        "Caminho Médio": caminho_medio,
        "Diâmetro": diametro
    }
