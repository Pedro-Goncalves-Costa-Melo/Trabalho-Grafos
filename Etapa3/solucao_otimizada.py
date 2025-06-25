import copy
from solucao import Rota


def calcular_custo_total_solucao(solucao):
    return sum(rota.custo_total for rota in solucao)


def two_opt_single_improvement(solucao_original, grafo):
    melhor_solucao = copy.deepcopy(solucao_original)
    melhor_custo = calcular_custo_total_solucao(melhor_solucao)

    for i in range(len(melhor_solucao)):
        rota1 = melhor_solucao[i]
        caminho1 = rota1.caminho

        if len(caminho1) < 4:  # Precisa de pelo menos 4 nós para trocar 2 arestas
            continue

        for j in range(1, len(caminho1) - 2):
            for k in range(j + 2, len(caminho1)):
                # Realiza a troca 2-opt
                novo_caminho = caminho1[:j] + caminho1[j:k][::-1] + caminho1[k:]

                # Calcula o custo do novo caminho
                novo_custo_rota = 0
                for l in range(1, len(novo_caminho)):
                    novo_custo_rota += grafo.obterDistanciaMinima(
                        novo_caminho[l - 1], novo_caminho[l]
                    )

                # Se a nova rota for melhor, atualiza e retorna
                if novo_custo_rota < rota1.custo_total:
                    # Cria uma nova rota com o caminho otimizado
                    nova_rota = Rota(rota1.id, rota1.deposito)
                    nova_rota.caminho = novo_caminho
                    nova_rota.demanda_total = rota1.demanda_total  # Demanda não muda
                    nova_rota.custo_total = novo_custo_rota
                    nova_rota.servicos_atendidos = rota1.servicos_atendidos
                    nova_rota.detalhes_visitas = rota1.detalhes_visitas

                    solucao_melhorada = copy.deepcopy(melhor_solucao)
                    solucao_melhorada[i] = nova_rota

                    return solucao_melhorada  # Retorna a primeira melhoria encontrada

    return solucao_original  # Retorna a solução original se nenhuma melhoria for encontrada
