import os
from grafo import GrafoEtapa1
from solucao_inicial import path_scanning
from utils import ler_arquivos_dat, garantir_pasta_saida, formatar_saida, obter_clocks


def main():
    pasta_entrada = "./MCGRP"
    pasta_saida = "./respostas"
    garantir_pasta_saida(pasta_saida)
    arquivos = ler_arquivos_dat(pasta_entrada)
    for arquivo in arquivos:
        nome_instancia = os.path.splitext(os.path.basename(arquivo))[0]
        print(f"Resolvendo {nome_instancia}...")
        grafo = GrafoEtapa1()
        grafo.carregarDados(arquivo)
        clk_ini = obter_clocks()
        solucao, mapeamento_id = path_scanning(grafo)
        clk_fim = obter_clocks()
        clocks_ref = clk_fim - clk_ini
        clocks_sol = (
            clk_fim - clk_ini
        )  # Use clocks_ref = clocks_sol (ou ajuste se necessário)
        saida = formatar_saida(
            solucao, mapeamento_id, nome_instancia, clocks_ref, clocks_sol
        )
        saida_path = os.path.join(pasta_saida, f"sol-{nome_instancia}.dat")
        with open(saida_path, "w") as f:
            f.write(saida)
        print(f"Arquivo {saida_path} gerado.")


if __name__ == "__main__":
    main()
