# Trabalho Prático - Algoritmos em Grafos (GCC218/GCC262)

Este repositório contém a implementação do trabalho prático final das disciplinas GCC218 - Algoritmos em Grafos e GCC262 - Grafos e suas Aplicações da Universidade Federal de Lavras (UFLA), sob orientação do Prof. Mayron César O. Moreira.

## Introdução

O estudo de problemas de logística é fundamental para a otimização do fluxo de bens e serviços, visando maior eficiência e redução de custos. A análise detalhada desses processos permite identificar gargalos, otimizar rotas, gerenciar estoques e implementar tecnologias para aprimorar a tomada de decisões. Este trabalho foca em uma variação do Problema de Roteamento de Veículos em Arcos (CARP - Capacitated Arc Routing Problem), um problema clássico na área de otimização e logística.

## Definição do Problema

O problema abordado é uma variação do CARP, definido em um multigrafo conectado G = (V, E, A), onde:
*   `V`: Conjunto de nós (vértices), representando interseções ou locais.
*   `E`: Conjunto de arestas (vias de mão dupla).
*   `A`: Conjunto de arcos (vias de mão única).

Serviços são requeridos para subconjuntos de nós (`VR`), arestas (`ER`) e arcos (`AR`). O objetivo é encontrar um conjunto de rotas de veículos com custo mínimo, partindo e retornando a um nó depósito (`v0`), de forma que:
1.  Cada serviço (nó, aresta ou arco requerido) seja atendido exatamente uma vez por uma única rota.
2.  A demanda total de serviços atendidos por cada veículo não exceda sua capacidade (`Q`).
3.  O custo total das rotas seja minimizado.

## Estrutura do Projeto e Implementação

O projeto está dividido em etapas, conforme descrito no documento do trabalho. Este repositório contém as implementações desenvolvidas.

### Etapa 1: Pré-processamento e Análise de Dados

A primeira etapa focou na modelagem do problema, leitura dos dados de entrada e cálculo de estatísticas descritivas do grafo.

**Modelagem:**
*   Foi criada a classe `GrafoEtapa1` (nos arquivos `Etapa1/GrafoEtapa1.py` e `Etapa2/dados/grafo.py`) para representar o multigrafo.
*   A classe armazena informações como nome da instância, número de vértices, arestas, arcos, elementos requeridos (vértices, arestas, arcos), capacidade do veículo, depósito, e as estruturas de dados para vértices, arestas e arcos (utilizando sets e dicionários).
*   Uma matriz de adjacência (`adjMatrix`) é inicializada para representar os custos diretos entre os nós.

**Leitura de Dados:**
*   A função `carregarDados(path)` dentro da classe `GrafoEtapa1` é responsável por ler os arquivos de instância `.dat`.
*   Ela utiliza expressões regulares (`re`) e análise de seções para extrair informações como nome, capacidade, depósito, nós requeridos (`ReN.`), arestas requeridas (`ReE.`), arcos requeridos (`ReA.`), arcos não requeridos (`ARC`) e arestas não requeridas (`EDGE`).
*   Os dados lidos populam as estruturas de dados da classe `GrafoEtapa1`.

**Cálculo de Estatísticas:**
*   A função `calcularEstatisticas(grafo)` (presente em `Etapa1/GrafoEtapa1.py`) calcula diversas métricas sobre o grafo carregado, conforme solicitado no trabalho:
    *   Quantidade de Vértices (`numVertices`)
    *   Quantidade de Arestas (`numArestas`)
    *   Quantidade de Arcos (`numArcos`)
    *   Quantidade de Vértices Requeridos (calculado com base nos nós terminais de arestas/arcos requeridos)
    *   Quantidade de Arestas Requeridas (`numArestasReq`)
    *   Quantidade de Arcos Requeridos (`numArcosReq`)
    *   Densidade do Grafo
    *   Grau Mínimo e Máximo dos Vértices
    *   Intermediação (Betweenness Centrality - calculada de forma simplificada sobre os caminhos mínimos)
    *   Caminho Médio (Average Path Length)
    *   Diâmetro do Grafo

**Caminhos Mínimos:**
*   A classe implementa o algoritmo de Floyd-Warshall na função `calcularDistanciasMinimas()` para calcular a matriz de distâncias mínimas (`matrizDistancias`) e a matriz de predecessores (`matrizPredecessores`) entre todos os pares de vértices.
*   As funções `obterDistanciaMinima(origem, destino)` e `obterCaminhoMinimo(origem, destino)` utilizam essas matrizes para retornar informações específicas.

**Visualização:**
*   A função `modelarGrafo(grafo)` (em `Etapa1/GrafoEtapa1.py`) utiliza `matplotlib` para gerar uma visualização gráfica da instância do problema, diferenciando depósito, nós com serviço, nós comuns, arestas/arcos com e sem serviço.

### Etapa 2: Solução Inicial (Heurística Construtiva)

A segunda etapa focou no desenvolvimento de uma heurística construtiva para gerar uma solução inicial viável para o problema CARP.

**Implementação:**
*   O código referente a esta etapa encontra-se no diretório `Etapa2/dados/`.
*   O arquivo `solucao_inicial.py` contém a implementação da heurística *Path Scanning*.
*   O arquivo `main.py` orquestra a leitura das instâncias, a execução da heurística e a escrita dos arquivos de solução no formato especificado (`sol-nome_instancia.dat`).
*   O arquivo `utils.py` contém funções auxiliares para leitura de arquivos, formatação da saída e medição de tempo.

**Heurística Path Scanning:**
*   Esta heurística constrói rotas sequencialmente.
*   Inicia-se uma nova rota a partir do depósito.
*   Busca-se o serviço (aresta ou arco requerido) mais próximo do ponto atual da rota que ainda não foi atendido.
*   O veículo se desloca até o início do serviço pelo caminho mínimo, executa o serviço e se move para o final do serviço.
*   Este processo é repetido, adicionando serviços à rota atual, até que a capacidade do veículo seja atingida ou não haja mais serviços viáveis para adicionar.
*   Se a capacidade for atingida, o veículo retorna ao depósito pelo caminho mínimo e uma nova rota é iniciada.
*   O processo continua até que todos os serviços requeridos sejam atendidos.

## Como Executar

**Etapa 1 (Análise e Estatísticas):**
Para utilizar a classe `GrafoEtapa1` e calcular as estatísticas de uma instância:
1.  Certifique-se de ter Python instalado.
2.  Instale as dependências (se houver, como matplotlib): `pip install matplotlib`
3.  Você pode importar a classe `GrafoEtapa1` em um script Python:
    ```python
    from Etapa1.GrafoEtapa1 import GrafoEtapa1, calcularEstatisticas, modelarGrafo

    # Caminho para o arquivo da instância
    caminho_instancia = 'caminho/para/sua/instancia.dat'

    # Criar e carregar o grafo
    grafo = GrafoEtapa1()
    grafo.carregarDados(caminho_instancia)

    # Calcular estatísticas
    estatisticas = calcularEstatisticas(grafo)
    print("Estatísticas do Grafo:")
    for chave, valor in estatisticas.items():
        print(f"- {chave}: {valor}")

    # Opcional: Visualizar o grafo
    # modelarGrafo(grafo)
    ```

**Etapa 2 (Solução Inicial):**
Para executar a heurística Path Scanning e gerar os arquivos de solução:
1.  Navegue até o diretório `Etapa2/dados/`.
2.  Certifique-se de que a pasta com as instâncias (ex: `MCGRP`) está no mesmo nível.
3.  Execute o script principal:
    ```bash
    cd Etapa2/dados
    python main.py
    ```
4.  Os arquivos de solução (`sol-*.dat`) serão gerados na pasta `G28` (ou o nome definido em `main.py`).

## Dependências

*   Python 3.x
*   Matplotlib (para visualização da Etapa 1)

## Autores

*   Pedro Gonçalves Costa Melo
* Lucas Henrique Lopes Costa

