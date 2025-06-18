import copy


def _criar_mapa_info_servicos(grafo):
    """Cria um mapa de ID para informações do serviço (custo, demanda) uma única vez."""
    from solucao_inicial import construir_mapeamento_servico_id

    mapa_id_servico = construir_mapeamento_servico_id(grafo)
    info_servicos = {}

    for serv_info, serv_id in mapa_id_servico.items():
        tipo, chave = serv_info
        if tipo == "aresta":
            dados = grafo.arestas[frozenset(chave)]
            info_servicos[serv_id] = {
                "custo": dados["custo"],
                "demanda": dados["demanda"],
            }
        elif tipo == "arco":
            dados = grafo.arcos[chave]
            info_servicos[serv_id] = {
                "custo": dados["custo"],
                "demanda": dados["demanda"],
            }
        elif tipo == "nó":
            info_servicos[serv_id] = {"custo": 0, "demanda": 1}

    return info_servicos


def _recalcular_custo_rota(rota, grafo, info_servicos):
    """Recalcula o custo total de uma única rota, usando o mapa de infos pré-calculado."""
    custo_total = 0
    no_anterior = grafo.deposito

    if rota["detalhes"]:
        for servico in rota["detalhes"]:
            custo_total += grafo.obterDistanciaMinima(no_anterior, servico[2])
            custo_total += info_servicos[servico[1]]["custo"]
            no_anterior = servico[3]

    custo_total += grafo.obterDistanciaMinima(no_anterior, grafo.deposito)
    return custo_total


def busca_local(solucao_inicial, grafo):
    # 1. Pré-calcula as informações dos serviços para evitar recálculos repetidos.
    info_servicos = _criar_mapa_info_servicos(grafo)
    solucao_atual = copy.deepcopy(solucao_inicial)

    while True:
        custo_total_atual = sum(r["custo"] for r in solucao_atual)
        melhor_delta_custo = 0
        melhor_solucao_vizinha = None

        # Itera sobre todas as possibilidades de mover um serviço para outra posição
        for r1_idx in range(len(solucao_atual)):
            if not solucao_atual[r1_idx]["detalhes"]:
                continue

            for serv_idx in range(len(solucao_atual[r1_idx]["detalhes"])):
                for r2_idx in range(len(solucao_atual)):
                    for pos_insercao in range(
                        len(solucao_atual[r2_idx]["detalhes"]) + 1
                    ):

                        # Evita mover um serviço para a sua própria posição
                        if r1_idx == r2_idx and (
                            serv_idx == pos_insercao or serv_idx + 1 == pos_insercao
                        ):
                            continue

                        # 2. Usa deepcopy para criar uma simulação segura, evitando erros de cálculo de delta.
                        solucao_simulada = copy.deepcopy(solucao_atual)

                        servico_movido = solucao_simulada[r1_idx]["detalhes"].pop(
                            serv_idx
                        )
                        demanda_movida = info_servicos[servico_movido[1]]["demanda"]

                        # Validação de capacidade
                        if (
                            r1_idx != r2_idx
                            and solucao_simulada[r2_idx]["demanda"] + demanda_movida
                            > grafo.capacidade
                        ):
                            continue

                        # Atualiza demandas e insere o serviço na nova posição
                        solucao_simulada[r1_idx]["demanda"] -= demanda_movida

                        # Ajuste para inserção na mesma rota
                        if r1_idx == r2_idx and serv_idx < pos_insercao:
                            pos_insercao -= 1

                        solucao_simulada[r2_idx]["detalhes"].insert(
                            pos_insercao, servico_movido
                        )
                        solucao_simulada[r2_idx]["demanda"] += demanda_movida

                        # Recalcula o custo apenas das rotas alteradas na simulação
                        solucao_simulada[r1_idx]["custo"] = _recalcular_custo_rota(
                            solucao_simulada[r1_idx], grafo, info_servicos
                        )
                        if r1_idx != r2_idx:
                            solucao_simulada[r2_idx]["custo"] = _recalcular_custo_rota(
                                solucao_simulada[r2_idx], grafo, info_servicos
                            )

                        custo_total_simulado = sum(r["custo"] for r in solucao_simulada)
                        delta_custo = custo_total_simulado - custo_total_atual

                        # 3. Adiciona uma tolerância para evitar loops por imprecisão de ponto flutuante.
                        if delta_custo < melhor_delta_custo - 1e-9:
                            melhor_delta_custo = delta_custo
                            melhor_solucao_vizinha = solucao_simulada

        # Se uma solução vizinha melhor foi encontrada, atualiza a solução atual e continua o loop
        if melhor_solucao_vizinha:
            solucao_atual = [r for r in melhor_solucao_vizinha if r["detalhes"]]
            novo_custo_total = sum(r["custo"] for r in solucao_atual)
            print(
                f"Melhoria encontrada! Novo Custo Total: {novo_custo_total:.2f} (Delta: {melhor_delta_custo:.2f})"
            )
        else:
            # Se nenhum vizinho melhora a solução, a busca termina.
            print("Nenhuma melhoria encontrada. Busca local concluída.")
            break

    return solucao_atual
