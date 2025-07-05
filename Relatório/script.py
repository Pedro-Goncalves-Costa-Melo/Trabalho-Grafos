import os
import pandas as pd

def gerar_relatorio_excel(pasta_etapa2, pasta_etapa3, nome_arquivo_saida="relatorio_comparativo.xlsx"):
    """
    Gera um arquivo Excel comparando os resultados das Etapas 2 e 3.

    Args:
        pasta_etapa2 (str): Caminho para a pasta contendo os arquivos .dat da Etapa 2.
        pasta_etapa3 (str): Caminho para a pasta contendo os arquivos .dat da Etapa 3.
        nome_arquivo_saida (str): Nome do arquivo Excel a ser gerado.
    """
    dados_para_excel = []

    # Lista todos os arquivos .dat da pasta da Etapa 3 (assumindo que os nomes são os mesmos)
    arquivos_dat = [f for f in os.listdir(pasta_etapa3) if f.endswith('.dat')]
    arquivos_dat.sort() # Garante uma ordem consistente

    if not arquivos_dat:
        print(f"Nenhum arquivo .dat encontrado na pasta: {pasta_etapa3}")
        return

    print(f"Processando {len(arquivos_dat)} arquivos...")

    for nome_arquivo in arquivos_dat:
        caminho_etapa2 = os.path.join(pasta_etapa2, nome_arquivo)
        caminho_etapa3 = os.path.join(pasta_etapa3, nome_arquivo)

        custo_etapa2 = None
        custo_etapa3 = None
        clocks_etapa2 = None
        clocks_etapa3 = None

        # Ler dados da Etapa 2
        try:
            with open(caminho_etapa2, 'r') as f:
                custo_etapa2 = int(f.readline().strip())
        except FileNotFoundError:
            print(f"Aviso: Arquivo não encontrado para Etapa 2: {caminho_etapa2}")
        except Exception as e:
            print(f"Erro ao ler {caminho_etapa2}: {e}")

        # Ler dados da Etapa 3
        try:
            with open(caminho_etapa3, 'r') as f:
                linhas = f.readlines()
                if len(linhas) >= 4:
                    custo_etapa3 = int(linhas[0].strip())
                    clocks_etapa2 = int(linhas[2].strip()) # Terceira linha (índice 2)
                    clocks_etapa3 = int(linhas[3].strip()) # Quarta linha (índice 3)
                else:
                    print(f"Aviso: Arquivo {caminho_etapa3} tem menos de 4 linhas.")
        except FileNotFoundError:
            print(f"Aviso: Arquivo não encontrado para Etapa 3: {caminho_etapa3}")
        except Exception as e:
            print(f"Erro ao ler {caminho_etapa3}: {e}")

        dados_para_excel.append({
            "nome arquivo": nome_arquivo,
            "custo etapa 2": custo_etapa2,
            "custo etapa 3": custo_etapa3,
            "clocks etapa 2": clocks_etapa2,
            "clocks etapa 3": clocks_etapa3,
        })

    # Criar DataFrame e exportar para Excel
    df = pd.DataFrame(dados_para_excel)
    try:
        df.to_excel(nome_arquivo_saida, index=False)
        print(f"\nRelatório gerado com sucesso: {nome_arquivo_saida}")
    except Exception as e:
        print(f"Erro ao salvar o arquivo Excel: {e}")

# --- Exemplo de Uso ---
if __name__ == "__main__":
    # Defina os caminhos para suas pastas aqui
    # Exemplo: se as pastas 'etapa2' e 'etapa3' estiverem no mesmo diretório do script
    PASTA_ETAPA2 = "etapa2"
    PASTA_ETAPA3 = "etapa3"

    # Certifique-se de que as pastas existam para o teste
    # Você pode criar pastas e arquivos .dat de exemplo para testar
    # Ex:
    # os.makedirs(PASTA_ETAPA2, exist_ok=True)
    # os.makedirs(PASTA_ETAPA3, exist_ok=True)
    # with open(os.path.join(PASTA_ETAPA2, "BHW1.dat"), "w") as f: f.write("100\n...\n")
    # with open(os.path.join(PASTA_ETAPA3, "BHW1.dat"), "w") as f: f.write("80\n5\n12345\n67890\n...")

    gerar_relatorio_excel(PASTA_ETAPA2, PASTA_ETAPA3)