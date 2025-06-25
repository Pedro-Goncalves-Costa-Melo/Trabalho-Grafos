from solucao import Rota
import heapq


def obter_servicos_pendentes(grafo):
    servicos = []
    for node in grafo.VR:
        servicos.append(
            {"tipo": "nó", "id": node, "demanda": 1, "custo": 0, "info": node}
        )
    for edge in grafo.ER:
        dados = grafo.arestas[edge]
        u, v = tuple(edge)
        servicos.append(
            {
                "tipo": "aresta",
                "id": None,
                "u": u,
                "v": v,
                "demanda": dados["demanda"],
                "custo": dados["custo"],
                "info": edge,
            }
        )
    for arc in grafo.AR:
        dados = grafo.arcos[arc]
        u, v = arc
        servicos.append(
            {
                "tipo": "arco",
                "id": None,
                "u": u,
                "v": v,
                "demanda": dados["demanda"],
                "custo": dados["custo"],
                "info": arc,
            }
        )
    return servicos


def construir_mapeamento_servico_id(grafo):
    mapeamento = {}
    current_id = 1
    for node in sorted(grafo.VR):
        mapeamento[("nó", node)] = current_id
        current_id += 1
    for edge in sorted(grafo.ER, key=lambda e: (min(e), max(e))):
        mapeamento[("aresta", tuple(sorted(edge)))] = current_id
        current_id += 1
    for arc in sorted(grafo.AR):
        mapeamento[("arco", arc)] = current_id
        current_id += 1
    return mapeamento


def path_scanning(grafo):
    grafo.calcularDistanciasMinimas()
    servicos_pendentes = set()
    servico_info = {}

    # Adiciona serviços de arestas e arcos
    for edge in grafo.ER:
        servicos_pendentes.add(("aresta", tuple(sorted(edge))))
        servico_info[("aresta", tuple(sorted(edge)))] = {
            "demanda": grafo.arestas[edge]["demanda"],
            "custo": grafo.arestas[edge]["custo"],
            "extremos": tuple(sorted(edge)),
        }
    for arc in grafo.AR:
        servicos_pendentes.add(("arco", arc))
        servico_info[("arco", arc)] = {
            "demanda": grafo.arcos[arc]["demanda"],
            "custo": grafo.arcos[arc]["custo"],
            "extremos": arc,
        }

    # Adiciona serviços de nós, excluindo o depósito se ele não tiver demanda requerida
    for node in grafo.VR:
        # Verifica se o nó tem demanda requerida no arquivo de entrada
        node_demand = grafo.demanda_nos.get(
            node, 0
        )  # Pega a demanda do nó, 0 se não tiver
        if node_demand > 0:  # Só adiciona como serviço pendente se tiver demanda > 0
            servicos_pendentes.add(("nó", node))
            servico_info[("nó", node)] = {
                "demanda": node_demand,
                "custo": 0,
                "extremos": (node, node),
            }

    # print(f"DEBUG: Capacidade do veículo: {grafo.capacidade}")
    mapeamento_id = construir_mapeamento_servico_id(grafo)
    solucao = []
    deposito = grafo.deposito

    while servicos_pendentes:
        rota_atual = Rota(len(solucao) + 1, deposito)
        no_atual = deposito

        while True:
            melhor_servico = None
            melhor_caminho = None
            menor_custo_caminho = float("inf")

            for serv in servicos_pendentes:
                info = servico_info[serv]
                extremos = info["extremos"]
                demanda_servico = info["demanda"]

                if not rota_atual.pode_adicionar_servico(
                    demanda_servico, grafo.capacidade
                ):
                    continue

                if serv[0] == "nó":
                    caminho = grafo.obterCaminhoMinimo(no_atual, extremos[0])
                    dist = grafo.obterDistanciaMinima(no_atual, extremos[0])
                else:
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

                if dist < menor_custo_caminho:
                    melhor_servico = serv
                    melhor_caminho = caminho
                    menor_custo_caminho = dist

            if melhor_servico is None:
                break

            # Adiciona o caminho até o serviço
            if melhor_caminho and len(melhor_caminho) > 1:
                rota_atual.adicionar_caminho(melhor_caminho, grafo)

            # Passa o tipo de serviço diretamente do melhor_servico
            servico_para_adicionar = {
                "tipo": melhor_servico[0],
                "extremos": servico_info[melhor_servico]["extremos"],
                "demanda": servico_info[melhor_servico]["demanda"],
                "custo": servico_info[melhor_servico]["custo"],
            }
            rota_atual.adicionar_servico(servico_para_adicionar, mapeamento_id, grafo)
            servicos_pendentes.remove(melhor_servico)
            no_atual = rota_atual.caminho[-1]

        # Retorna ao depósito
        if no_atual != deposito:
            caminho_volta = grafo.obterCaminhoMinimo(no_atual, deposito)
            if caminho_volta and len(caminho_volta) > 1:
                rota_atual.adicionar_caminho(caminho_volta, grafo)

        solucao.append(rota_atual)

    return solucao, mapeamento_id
