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
    for node in grafo.VR:
        servicos_pendentes.add(("nó", node))
        servico_info[("nó", node)] = {
            "demanda": 1,
            "custo": 0,
            "extremos": (node, node),
        }
    mapeamento_id = construir_mapeamento_servico_id(grafo)
    solucao = []
    deposito = grafo.deposito

    while servicos_pendentes:
        rota = [deposito]
        carga = 0
        custo = 0
        servicos_rota = []
        detalhes_visitas = []
        no_atual = deposito
        visitados_este_veiculo = set()
        while True:
            melhor_servico = None
            melhor_caminho = None
            menor_custo = float("inf")
            for serv in servicos_pendentes:
                info = servico_info[serv]
                extremos = info["extremos"]
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
                        chegada = extremos[0]
                        outro_extremo = extremos[1]
                    else:
                        caminho = caminho2
                        dist = dist2
                        chegada = extremos[1]
                        outro_extremo = extremos[0]
                demanda = info["demanda"]
                if carga + demanda > grafo.capacidade:
                    continue
                if dist < menor_custo:
                    melhor_servico = serv
                    melhor_caminho = caminho
                    melhor_extremos = extremos
                    menor_custo = dist
            if melhor_servico is None:
                break
            if melhor_caminho:
                for i in range(1, len(melhor_caminho)):
                    custo += grafo.obterDistanciaMinima(
                        melhor_caminho[i - 1], melhor_caminho[i]
                    )
                    rota.append(melhor_caminho[i])
            info = servico_info[melhor_servico]
            demanda = info["demanda"]
            custo += info["custo"]
            carga += demanda
            servicos_rota.append(melhor_servico)
            visitados_este_veiculo.add(melhor_servico)
            if melhor_servico[0] == "nó":
                id_servico = mapeamento_id[melhor_servico]
                detalhes_visitas.append(
                    ("S", id_servico, melhor_extremos[0], melhor_extremos[0])
                )
            elif melhor_servico[0] == "aresta":
                id_servico = mapeamento_id[melhor_servico]
                u, v = melhor_extremos
                if len(rota) >= 2:
                    if rota[-2] == u and rota[-1] == v:
                        detalhes_visitas.append(("S", id_servico, u, v))
                    else:
                        detalhes_visitas.append(("S", id_servico, v, u))
                else:
                    detalhes_visitas.append(("S", id_servico, u, v))
            elif melhor_servico[0] == "arco":
                id_servico = mapeamento_id[melhor_servico]
                u, v = melhor_extremos
                if len(rota) >= 2:
                    if rota[-2] == u and rota[-1] == v:
                        detalhes_visitas.append(("S", id_servico, u, v))
                    else:
                        detalhes_visitas.append(("S", id_servico, v, u))
                else:
                    detalhes_visitas.append(("S", id_servico, u, v))
            servicos_pendentes.remove(melhor_servico)
            no_atual = rota[-1]
        if no_atual != deposito:
            caminho_volta = grafo.obterCaminhoMinimo(no_atual, deposito)
            if caminho_volta:
                for i in range(1, len(caminho_volta)):
                    custo += grafo.obterDistanciaMinima(
                        caminho_volta[i - 1], caminho_volta[i]
                    )
                    rota.append(caminho_volta[i])
        solucao.append(
            {
                "rota": rota,
                "servicos_atendidos": servicos_rota,
                "demanda": carga,
                "custo": custo,
                "detalhes": detalhes_visitas,
            }
        )
    return solucao, mapeamento_id
