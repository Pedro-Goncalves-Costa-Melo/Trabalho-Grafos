from solucao import (
    Rota,
)  # Importa a classe Rota, responsável por armazenar e manipular rotas na solução
import heapq  # Importa heapq (usado para filas de prioridade, mas não é usado neste código diretamente)


# Função que retorna todos os serviços pendentes do grafo (nós, arestas e arcos que precisam ser atendidos)
def obter_servicos_pendentes(grafo):
    servicos = []

    # Adiciona todos os NÓS que requerem serviço (VR) como serviços pendentes
    for node in grafo.VR:
        servicos.append(
            {
                "tipo": "nó",  # Tipo do serviço é nó
                "id": node,  # ID do nó
                "demanda": 1,  # Demanda padrão (ou poderia pegar do grafo.demanda_nos)
                "custo": 0,  # Custo para atender nó (aqui considerado zero)
                "info": node,  # Informação adicional (id do nó)
            }
        )
    # Adiciona todas as ARESTAS que requerem serviço (ER)
    for edge in grafo.ER:
        dados = grafo.arestas[edge]  # Busca os dados da aresta (custo, demanda...)
        u, v = tuple(edge)
        servicos.append(
            {
                "tipo": "aresta",  # Tipo de serviço: aresta
                "id": None,
                "u": u,  # Extremos da aresta
                "v": v,
                "demanda": dados["demanda"],  # Demanda da aresta
                "custo": dados["custo"],  # Custo para servir essa aresta
                "info": edge,  # Informação adicional (frozenset dos nós)
            }
        )
    # Adiciona todos os ARCOS que requerem serviço (AR)
    for arc in grafo.AR:
        dados = grafo.arcos[arc]  # Busca os dados do arco (custo, demanda...)
        u, v = arc
        servicos.append(
            {
                "tipo": "arco",  # Tipo de serviço: arco (direcionado)
                "id": None,
                "u": u,
                "v": v,
                "demanda": dados["demanda"],  # Demanda do arco
                "custo": dados["custo"],  # Custo do arco
                "info": arc,  # Informação adicional (tupla dos nós)
            }
        )
    return servicos  # Retorna lista de todos os serviços pendentes


# Função para criar um mapeamento único de identificador para cada serviço (nó, aresta, arco)
def construir_mapeamento_servico_id(grafo):
    mapeamento = {}
    current_id = (
        1  # Começa os ids em 1 (pode ser útil para exportar para sistemas externos)
    )
    # Mapeia nós
    for node in sorted(grafo.VR):
        mapeamento[("nó", node)] = current_id
        current_id += 1
    # Mapeia arestas (com tupla ordenada para garantir consistência)
    for edge in sorted(grafo.ER, key=lambda e: (min(e), max(e))):
        mapeamento[("aresta", tuple(sorted(edge)))] = current_id
        current_id += 1
    # Mapeia arcos (direcionados, então ordem importa)
    for arc in sorted(grafo.AR):
        mapeamento[("arco", arc)] = current_id
        current_id += 1
    return mapeamento  # Retorna o dicionário: chave = (tipo, info), valor = id inteiro


# Algoritmo path scanning (estratégia gulosa para criar rotas)
def path_scanning(grafo):
    grafo.calcularDistanciasMinimas()  # Calcula a matriz de distâncias mínimas entre todos os pares de nós

    servicos_pendentes = (
        set()
    )  # Conjunto para armazenar os serviços ainda não atendidos
    servico_info = {}  # Informações detalhadas de cada serviço

    # Adiciona serviços de arestas (que requerem serviço)
    for edge in grafo.ER:
        servicos_pendentes.add(
            ("aresta", tuple(sorted(edge)))
        )  # Armazena com tupla ordenada
        servico_info[("aresta", tuple(sorted(edge)))] = {
            "demanda": grafo.arestas[edge]["demanda"],
            "custo": grafo.arestas[edge]["custo"],
            "extremos": tuple(sorted(edge)),  # Extremos da aresta (ordem não importa)
        }
    # Adiciona serviços de arcos (direcionados)
    for arc in grafo.AR:
        servicos_pendentes.add(("arco", arc))
        servico_info[("arco", arc)] = {
            "demanda": grafo.arcos[arc]["demanda"],
            "custo": grafo.arcos[arc]["custo"],
            "extremos": arc,  # Extremos do arco (ordem importa)
        }
    # Adiciona serviços de nós que realmente têm demanda (>0)
    for node in grafo.VR:
        node_demand = grafo.demanda_nos.get(
            node, 0
        )  # Busca demanda do nó (ou 0 se não houver)
        if node_demand > 0:
            servicos_pendentes.add(("nó", node))
            servico_info[("nó", node)] = {
                "demanda": node_demand,
                "custo": 0,
                "extremos": (node, node),  # Extremos do nó é ele mesmo
            }

    # Cria o mapeamento id para os serviços (útil para identificações únicas)
    mapeamento_id = construir_mapeamento_servico_id(grafo)
    solucao = []  # Lista onde serão salvas as rotas geradas
    deposito = grafo.deposito  # Nó de início/fim das rotas

    # Enquanto houver serviços pendentes, monta uma nova rota
    while servicos_pendentes:
        rota_atual = Rota(len(solucao) + 1, deposito)  # Cria nova rota (id sequencial)
        no_atual = deposito  # Sempre começa do depósito

        # Dentro da rota atual, adiciona o serviço mais próximo possível que caiba na capacidade
        while True:
            melhor_servico = (
                None  # Vai guardar o melhor serviço a ser adicionado na rota atual
            )
            melhor_caminho = None  # Vai guardar o melhor caminho até esse serviço
            menor_custo_caminho = float("inf")  # Começa com infinito

            # Analisa todos os serviços pendentes
            for serv in servicos_pendentes:
                info = servico_info[serv]
                extremos = info["extremos"]
                demanda_servico = info["demanda"]

                # Só pode adicionar serviço se não exceder capacidade da rota
                if not rota_atual.pode_adicionar_servico(
                    demanda_servico, grafo.capacidade
                ):
                    continue

                # Para nós: caminho e custo direto até o nó - Define qual caminho vai usar
                if serv[0] == "nó":
                    caminho = grafo.obterCaminhoMinimo(no_atual, extremos[0])
                    dist = grafo.obterDistanciaMinima(no_atual, extremos[0])
                else:
                    # Para arestas/arcos: calcula caminho e custo até cada extremo,
                    # e pega o de menor distância
                    caminho1 = grafo.obterCaminhoMinimo(no_atual, extremos[0])
                    dist1 = grafo.obterDistanciaMinima(no_atual, extremos[0])
                    caminho2 = grafo.obterCaminhoMinimo(no_atual, extremos[1])
                    dist2 = grafo.obterDistanciaMinima(no_atual, extremos[1])

                    if dist1 <= dist2:
                        caminho = caminho1
                        dist = dist1
                    else:
                        caminho = caminho2
                        dist = dist2

                # Se este serviço está mais perto do que os outros já analisados, atualiza
                if dist < menor_custo_caminho:
                    melhor_servico = serv
                    melhor_caminho = caminho
                    menor_custo_caminho = dist

            # Se não encontrou nenhum serviço possível (capacidade cheia ou todos longe demais), termina a rota
            if melhor_servico is None:
                break

            # Adiciona ao caminho da rota o trajeto até o serviço escolhido
            if melhor_caminho and len(melhor_caminho) > 1:
                rota_atual.adicionar_caminho(melhor_caminho, grafo)

            # Prepara um dicionário com os dados do serviço para adicionar na rota
            servico_para_adicionar = {
                "tipo": melhor_servico[0],
                "extremos": servico_info[melhor_servico]["extremos"],
                "demanda": servico_info[melhor_servico]["demanda"],
                "custo": servico_info[melhor_servico]["custo"],
            }
            rota_atual.adicionar_servico(servico_para_adicionar, mapeamento_id, grafo)
            servicos_pendentes.remove(
                melhor_servico
            )  # Remove serviço da lista de pendentes
            no_atual = rota_atual.caminho[-1]  # Atualiza posição atual do veículo

        # Quando terminar de adicionar serviços à rota, volta para o depósito se não estiver lá
        if no_atual != deposito:
            caminho_volta = grafo.obterCaminhoMinimo(no_atual, deposito)
            if caminho_volta and len(caminho_volta) > 1:
                rota_atual.adicionar_caminho(caminho_volta, grafo)

        solucao.append(rota_atual)  # Salva a rota pronta na lista de solução

    return (
        solucao,
        mapeamento_id,
    )  # Retorna lista de rotas e o mapeamento de serviços por id
