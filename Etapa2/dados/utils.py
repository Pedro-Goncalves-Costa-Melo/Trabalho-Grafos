import os
import time


def ler_arquivos_dat(pasta):
    arquivos = []
    for nome in os.listdir(pasta):
        if nome.endswith(".dat"):
            arquivos.append(os.path.join(pasta, nome))
    return arquivos


def garantir_pasta_saida(pasta):
    if not os.path.exists(pasta):
        os.makedirs(pasta)


def formatar_saida(solucao, mapeamento_id, nome_instancia, clocks_ref=0, clocks_sol=0):
    # Custo total e número de rotas
    custo_total = sum(r["custo"] for r in solucao)
    total_rotas = len(solucao)
    # Formata as linhas de rota
    linhas_rotas = []
    for idx, rota in enumerate(solucao, 1):
        demanda = rota["demanda"]
        custo_r = int(rota["custo"])
        detalhes = rota["detalhes"]
        total_visitas = 2 + len(detalhes)  # depósito ida e volta + serviços
        linha = f" 0 1 {idx} {demanda} {custo_r}  {total_visitas} (D 0,1,1)"
        for s in detalhes:
            # (S id, u, v)
            linha += f" (S {s[1]},{s[2]},{s[3]})"
        linha += " (D 0,1,1)"
        linhas_rotas.append(linha)
    # Monta saída completa
    saida = (
        f"{int(custo_total)}\n"
        f"{total_rotas}\n"
        f"{clocks_ref}\n"
        f"{clocks_sol}\n" + "\n".join(linhas_rotas)
    )
    return saida


def obter_clocks():
    # Retorna tempo em clocks (simulação baseada em time.monotonic_ns)
    return time.monotonic_ns() // 1000  # microsegundos (ajuste se necessário)
