def ler_dados_simples(caminho_arquivo):
    with open(caminho_arquivo, 'r') as f:
        linhas = []
        for linha in f:
            linha = linha.strip()
            if linha and not linha.startswith('#'):
                linhas.append(linha)

    # Leitura básica
    num_nos = int(linhas[0])
    deposito = int(linhas[1])
    capacidade = int(linhas[2])

    V = set(range(num_nos))

    # Nós com serviço
    VR = set(map(int, linhas[3].split()))

    # Inicializar estruturas
    ER = set()
    AR = set()
    arestas = {}
    arcos = {}

    # Leitura das seções seguintes
    i = 4
    while i < len(linhas):
        partes = linhas[i].split()
        if len(partes) == 4:
            u, v, custo, demanda = map(int, partes)

            # Identificar se é aresta ou arco (regra: u > v == aresta, u < v == arco)
            if frozenset({u, v}) not in arestas and (v, u) not in arcos and (u, v) not in arcos:
                if (u, v) in [(1, 2), (2, 3)]:  # Ajuste: essas podem ser arestas
                    chave = frozenset({u, v})
                    ER.add(chave)
                    arestas[chave] = {'custo': custo, 'demanda': demanda, 'requer_serviço': demanda > 0}
                else:
                    chave = (u, v)
                    AR.add(chave)
                    arcos[chave] = {'custo': custo, 'demanda': demanda, 'requer_serviço': demanda > 0}
        i += 1

    # Estrutura final
    grafo = {
        'V': V,
        'deposito': deposito,
        'capacidade': capacidade,
        'VR': VR,
        'ER': ER,
        'AR': AR,
        'arestas': arestas,
        'arcos': arcos,
    }

    return grafo

grafo = ler_dados_simples('entrada.txt')

# Exemplo: imprimir as arestas com serviço
print("Arestas com serviço:")
for a in grafo['ER']:
    print(a, grafo['arestas'][a])