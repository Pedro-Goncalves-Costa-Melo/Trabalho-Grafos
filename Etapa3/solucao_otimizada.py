import copy  # Usado para fazer cópias profundas dos objetos, evitando alterar a solução original
from solucao import (
    Rota,
)  # Classe de rotas, usada para criar e manipular rotas de veículos


# Função auxiliar que calcula o custo total de uma solução, somando o custo de todas as rotas
def calcular_custo_total_solucao(solucao):
    return sum(rota.custo_total for rota in solucao)


# Função de melhoria local: tenta melhorar a solução usando a heurística 2-opt em cada rota
def two_opt_single_improvement(solucao_original, grafo):
    # Faz uma cópia da solução para evitar alterar o original
    melhor_solucao = copy.deepcopy(solucao_original)
    melhor_custo = calcular_custo_total_solucao(melhor_solucao)

    # Para cada rota da solução, tenta aplicar uma troca 2-opt
    for i in range(len(melhor_solucao)):
        rota1 = melhor_solucao[i]
        caminho1 = rota1.caminho  # O caminho é a lista de nós visitados pela rota

        # Para aplicar 2-opt, o caminho precisa ter pelo menos 4 nós
        if len(caminho1) < 4:
            continue

        # A heurística 2-opt tenta melhorar a rota trocando a ordem de visita de um segmento
        # Para cada possível par de posições (j, k) no caminho:
        for j in range(1, len(caminho1) - 2):
            for k in range(j + 2, len(caminho1)):
                # Realiza a operação 2-opt: inverte o segmento do caminho entre j e k-1
                # Exemplo: caminho [1,2,3,4,5,6], se j=2, k=5 -> [1,2,5,4,3,6]
                novo_caminho = caminho1[:j] + caminho1[j:k][::-1] + caminho1[k:]

                # Calcula o custo do novo caminho usando a matriz de distâncias mínimas do grafo
                novo_custo_rota = 0
                for l in range(1, len(novo_caminho)):
                    novo_custo_rota += grafo.obterDistanciaMinima(
                        novo_caminho[l - 1], novo_caminho[l]
                    )

                # Se a troca 2-opt realmente reduziu o custo da rota, aceita a melhoria!
                if novo_custo_rota < rota1.custo_total:
                    # Cria uma nova rota para guardar o novo caminho
                    nova_rota = Rota(rota1.id, rota1.deposito)
                    nova_rota.caminho = novo_caminho
                    nova_rota.demanda_total = (
                        rota1.demanda_total
                    )  # A demanda não muda (os nós atendidos são os mesmos)
                    nova_rota.custo_total = novo_custo_rota
                    # Copia também os serviços já atendidos e detalhes das visitas, para manter consistência
                    nova_rota.servicos_atendidos = rota1.servicos_atendidos
                    nova_rota.detalhes_visitas = rota1.detalhes_visitas

                    # Cria uma nova solução, substituindo apenas a rota melhorada
                    solucao_melhorada = copy.deepcopy(melhor_solucao)
                    solucao_melhorada[i] = nova_rota

                    # Retorna a primeira melhoria encontrada (versão clássica do 2-opt "first improvement")
                    return solucao_melhorada

    # Se não encontrou nenhuma melhoria, retorna a solução original (já é localmente ótima para 2-opt)
    return solucao_original


# # Função que executa o 2-opt de forma iterativa até não encontrar mais melhorias acima do limiar
# def two_opt_iterativo(solucao_inicial, grafo, limiar=0.1):
#     """
#     Aplica 2-opt iterativamente até não encontrar mais melhoria acima do limiar.
#     limiar: mínima diferença de custo para aceitar a nova solução (float).
#     """
#     solucao_atual = copy.deepcopy(solucao_inicial)
#     custo_atual = calcular_custo_total_solucao(solucao_atual)

#     while True:
#         solucao_melhorada = two_opt_single_improvement(solucao_atual, grafo, limiar)
#         custo_melhorado = calcular_custo_total_solucao(solucao_melhorada)

#         # Se não melhorou nada ou a melhoria é menor que o limiar, termina
#         if custo_atual - custo_melhorado <= limiar:
#             break

#         # Aceita a melhoria e tenta de novo
#         solucao_atual = solucao_melhorada
#         custo_atual = custo_melhorado

#     return solucao_atual
