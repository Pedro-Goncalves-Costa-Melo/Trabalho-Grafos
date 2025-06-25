class Rota:
    def __init__(self, id_rota, deposito):
        self.id = id_rota
        self.deposito = deposito
        self.caminho = [deposito]
        self.demanda_total = 0
        self.custo_total = 0
        self.servicos_atendidos = []  # Lista de serviços (tuplas: tipo, id_original)
        self.detalhes_visitas = []  # Para o formato de saída (S id, u, v)

    def adicionar_servico(self, servico_info, mapeamento_id, grafo):
        # servico_info: {"tipo": "aresta/arco/nó", "extremos": (u,v), "demanda": X, "custo": Y}
        # mapeamento_id: dicionário para obter o ID do serviço para a saída
        # grafo: para obter distâncias e custos de arestas/arcos

        # Adiciona a demanda e o custo do serviço
        self.demanda_total += servico_info["demanda"]
        self.custo_total += servico_info["custo"]

        # Adiciona o serviço à lista de serviços atendidos
        self.servicos_atendidos.append(servico_info)

        # Adiciona os detalhes da visita para o formato de saída
        tipo_servico = servico_info["tipo"]
        extremos = servico_info["extremos"]
        id_servico_formatado = (
            mapeamento_id[(tipo_servico, extremos)]
            if tipo_servico != "nó"
            else mapeamento_id[(tipo_servico, extremos[0])]
        )

        if tipo_servico == "nó":
            self.detalhes_visitas.append(
                ("S", id_servico_formatado, extremos[0], extremos[0])
            )
        elif tipo_servico == "aresta" or tipo_servico == "arco":
            # Precisa verificar a ordem de visita para imprimir corretamente (u,v) ou (v,u)
            # Por enquanto, vamos assumir a ordem original, mas isso pode precisar de ajuste
            # dependendo de como o path_scanning realmente percorre.
            self.detalhes_visitas.append(
                ("S", id_servico_formatado, extremos[0], extremos[1])
            )

    def adicionar_caminho(self, caminho, grafo):
        # Adiciona os nós do caminho à rota e atualiza o custo
        for i in range(1, len(caminho)):
            self.caminho.append(caminho[i])
            self.custo_total += grafo.obterDistanciaMinima(caminho[i - 1], caminho[i])

    def pode_adicionar_servico(self, demanda_servico, capacidade_veiculo):
        return self.demanda_total + demanda_servico <= capacidade_veiculo

    def __str__(self):
        return f"Rota ID: {self.id}, Demanda: {self.demanda_total}, Custo: {self.custo_total}, Serviços: {len(self.servicos_atendidos)}"
