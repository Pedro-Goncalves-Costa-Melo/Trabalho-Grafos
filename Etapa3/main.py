import os
from grafo import GrafoEtapa1
from solucao_inicial import path_scanning
from utils import ler_arquivos_dat, garantir_pasta_saida, formatar_saida, obter_clocks
from busca_local import busca_local  # <<<--- 1. IMPORTAR A NOVA FUNÇÃO


def main():
    pasta_entrada = "./MCGRP"
    pasta_saida = "./G28"
    garantir_pasta_saida(pasta_saida)
    arquivos = ler_arquivos_dat(pasta_entrada)
    for arquivo in arquivos:
        nome_instancia = os.path.splitext(os.path.basename(arquivo))[0]
        print(f"\nResolvendo {nome_instancia}...")
        grafo = GrafoEtapa1()
        grafo.carregarDados(arquivo)

        # --- GERAÇÃO DA SOLUÇÃO INICIAL (Fase 2) ---
        print("Gerando solução inicial com Path Scanning...")
        clk_ini_construtiva = obter_clocks()
        solucao_inicial, mapeamento_id = path_scanning(grafo)
        clk_fim_construtiva = obter_clocks()

        custo_inicial = sum(r["custo"] for r in solucao_inicial)
        print(f"Custo inicial: {custo_inicial:.2f}, Rotas: {len(solucao_inicial)}")

        # --- APRIMORAMENTO COM BUSCA LOCAL (Fase 3) ---
        print("Aprimorando solução com Busca Local...")
        clk_ini_busca = obter_clocks()
        solucao_final = busca_local(solucao_inicial, grafo)
        clk_fim_busca = obter_clocks()
        # ---------------------------------------------------

        custo_final = sum(r["custo"] for r in solucao_final)
        print(f"Custo final: {custo_final:.2f}, Rotas: {len(solucao_final)}")

        # O tempo de solução total é a soma das duas fases
        clocks_sol = (clk_fim_construtiva - clk_ini_construtiva) + (
            clk_fim_busca - clk_ini_busca
        )
        clocks_ref = clocks_sol  # Para este projeto, usamos o mesmo tempo.

        # <<<--- 3. USAR A SOLUÇÃO FINAL PARA GERAR A SAÍDA
        saida = formatar_saida(
            solucao_final, mapeamento_id, nome_instancia, clocks_ref, clocks_sol
        )
        saida_path = os.path.join(pasta_saida, f"sol-{nome_instancia}.dat")
        with open(saida_path, "w") as f:
            f.write(saida)
        print(f"Arquivo {saida_path} gerado.")


if __name__ == "__main__":
    main()
