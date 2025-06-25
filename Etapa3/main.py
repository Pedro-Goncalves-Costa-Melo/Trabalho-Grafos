import os
from grafo import GrafoEtapa1
from solucao_inicial import path_scanning
from solucao_otimizada import two_opt_single_improvement, calcular_custo_total_solucao
from utils import ler_arquivos_dat, garantir_pasta_saida, formatar_saida, obter_clocks


def main():
    pasta_entrada = "./MCGRP"
    pasta_saida = "./G28"
    garantir_pasta_saida(pasta_saida)
    arquivos = ler_arquivos_dat(pasta_entrada)
    # print(f"Arquivos encontrados: {arquivos}")
    for arquivo in arquivos:
        nome_instancia = os.path.splitext(os.path.basename(arquivo))[0]
        print(f"Resolvendo {nome_instancia}...")
        grafo = GrafoEtapa1()
        grafo.carregarDados(arquivo)

        # Executa a solução inicial
        clk_ini_path_scanning = obter_clocks()
        solucao_inicial, mapeamento_id = path_scanning(grafo)
        clk_fim_path_scanning = obter_clocks()
        clocks_path_scanning = clk_fim_path_scanning - clk_ini_path_scanning
        custo_inicial = calcular_custo_total_solucao(solucao_inicial)

        # Aplica a otimização 2-opt
        clk_ini_2opt = obter_clocks()
        solucao_otimizada = two_opt_single_improvement(solucao_inicial, grafo)
        clk_fim_2opt = obter_clocks()
        clocks_2opt = clk_fim_2opt - clk_ini_2opt

        # Calcula o custo total da solução otimizada
        custo_otimizado = calcular_custo_total_solucao(solucao_otimizada)
        delta_custo = custo_inicial - custo_otimizado

        print(f"  Custo inicial: {custo_inicial}")
        print(f"  Custo otimizado: {custo_otimizado}")
        print(f"  Delta de diferença: {delta_custo}")

        # Formata a saída com a solução otimizada
        saida = formatar_saida(
            solucao_otimizada,
            mapeamento_id,
            nome_instancia,
            clocks_path_scanning,
            clocks_2opt,
        )
        saida_path = os.path.join(pasta_saida, f"sol-{nome_instancia}.dat")
        with open(saida_path, "w") as f:
            f.write(saida)
        print(f"Arquivo {saida_path} gerado com solução otimizada.\n")


if __name__ == "__main__":
    main()
