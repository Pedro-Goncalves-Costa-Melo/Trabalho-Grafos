# Conjunto de nós (intersecções ou esquinas)
V = {0, 1, 2, 3}

# Nó 0 é o depósito
deposito = 0

# Capacidade dos veículos
Q = 10

# Subconjunto de nós com serviço requerido
VR = {1}

# Arestas (vias bidirecionais): representadas com frozenset
edges = {
    frozenset({1, 2}): {'custo': 3, 'demanda': 2, 'requer_serviço': True},
    frozenset({2, 3}): {'custo': 4, 'demanda': 0, 'requer_serviço': False},
}

# Subconjunto de arestas com serviço
ER = {frozenset({1, 2})}

# Arcos (vias de mão única): representados com tuplas ordenadas (i, j)
arcs = {
    (0, 1): {'custo': 5, 'demanda': 3, 'requer_serviço': True},
    (1, 2): {'custo': 2, 'demanda': 0, 'requer_serviço': False},
    (2, 0): {'custo': 4, 'demanda': 1, 'requer_serviço': True},
}

# Subconjunto de arcos com serviço
AR = {(0, 1), (2, 0)}

# Representação geral do multigrafo G = (V, E, A)
G = {
    'nós': V,
    'depósito': deposito,
    'capacidade_veiculo': Q,
    'arestas': edges,
    'arcos': arcs,
    'VR': VR,
    'ER': ER,
    'AR': AR,
}

print(G)