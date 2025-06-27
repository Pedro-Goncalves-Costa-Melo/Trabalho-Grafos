# Trabalho Prático - Algoritmos em Grafos (GCC218/GCC262)

Este repositório contém a implementação do trabalho prático final das disciplinas GCC218 - Algoritmos em Grafos e GCC262 - Grafos e suas Aplicações da Universidade Federal de Lavras (UFLA), sob orientação do Prof. Mayron César O. Moreira.

## Introdução

O estudo de problemas de logística é crucial para otimizar o fluxo de bens e serviços, resultando em maior eficiência e redução de custos para empresas e consumidores. A análise detalhada de processos logísticos permite identificar gargalos, melhorar o planejamento de rotas, gerenciar estoques de forma mais eficaz e implementar tecnologias que aprimoram a tomada de decisões.

Este trabalho foca em uma variação do Problema de Roteamento de Veículos em Arcos (CARP - Capacitated Arc Routing Problem), um problema clássico na área de otimização e logística, expandindo-o para incluir também serviços em nós e arcos direcionados.

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
*   Foi criada a classe `GrafoEtapa1` para representar o multigrafo.
*   A classe armazena informações como nome da instância, número de vértices, arestas, arcos, elementos requeridos (vértices, arestas, arcos), capacidade do veículo, depósito, e as estruturas de dados para vértices, arestas e arcos (utilizando sets e dicionários).
*   Uma matriz de adjacência (`adjMatrix`) é inicializada para representar os custos diretos entre os nós.

**Leitura de Dados:**
*   A função `carregarDados(path)` dentro da classe `GrafoEtapa1` é responsável por ler os arquivos de instância `.dat`.
*   Ela utiliza expressões regulares (`re`) e análise de seções para extrair informações como nome, capacidade, depósito, nós requeridos (`ReN.`), arestas requeridas (`ReE.`), arcos requeridos (`ReA.`), arcos não requeridos (`ARC`) e arestas não requeridas (`EDGE`).
*   Os dados lidos populam as estruturas de dados da classe `GrafoEtapa1`.

**Cálculo de Estatísticas:**
*   A função `calcularEstatisticas(grafo)` calcula diversas métricas sobre o grafo carregado, conforme solicitado no trabalho:
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

### Etapa 2: Solução Inicial (Heurística Construtiva)

A segunda etapa focou no desenvolvimento de uma heurística construtiva para gerar uma solução inicial viável para o problema CARP.

**Implementação:**
*   O algoritmo implementado é uma variação da heurística *Path Scanning*.
*   A função `path_scanning(grafo)` constrói rotas sequencialmente, iniciando no depósito e adicionando serviços até que a capacidade do veículo seja atingida.
*   Para cada serviço pendente, o algoritmo calcula o custo de deslocamento até ele e escolhe o de menor custo.
*   Após atender todos os serviços possíveis dentro da capacidade, o veículo retorna ao depósito e uma nova rota é iniciada.

**Estrutura da Solução:**
*   A classe `Rota` representa uma rota de veículo, armazenando o caminho percorrido, demanda total, custo total e serviços atendidos.
*   A solução final é uma lista de objetos `Rota`, cada um representando uma rota completa (depósito → serviços → depósito).

### Etapa 3: Métodos de Melhoria (Busca Local)

A terceira etapa focou no aprimoramento da solução inicial através da implementação de um algoritmo de busca local.

**Algoritmo de Melhoria:**
*   Foi implementado o algoritmo **2-opt** (Two-Opt) como método de busca local para otimizar as rotas geradas na etapa anterior.
*   O 2-opt é uma técnica clássica de otimização de rotas que consiste em remover duas arestas não adjacentes de uma rota e reconectar os segmentos resultantes de uma maneira diferente, potencialmente reduzindo o custo total.

**Implementação da Busca Local:**
*   A função `two_opt_single_improvement(solucao_original, grafo)` implementa a estratégia de "primeira melhoria" (first improvement), onde a primeira modificação que resulta em uma redução de custo é imediatamente aceita.
*   Para cada rota na solução:
    1. O algoritmo considera todas as possíveis trocas 2-opt (inversão de segmentos do caminho).
    2. Calcula o custo da nova rota após cada troca potencial.
    3. Se uma troca resultar em redução de custo, a modificação é aplicada e a função retorna a solução melhorada.
*   O processo é aplicado a cada rota individualmente, mantendo a atribuição de serviços às rotas originais.

**Integração com a Solução Inicial:**
*   O arquivo `main.py` orquestra o processo completo:
    1. Carrega os dados da instância.
    2. Gera uma solução inicial usando o algoritmo Path Scanning.
    3. Aplica a otimização 2-opt à solução inicial.
    4. Calcula e exibe a diferença de custo entre a solução inicial e a otimizada.
    5. Formata e salva a solução otimizada no formato especificado.

**Melhorias Implementadas:**
*   A classe `GrafoEtapa1` foi aprimorada para armazenar a demanda dos nós (`demanda_nos`), permitindo um tratamento mais preciso dos serviços em nós.
*   O método `_inicializarMatrizAdjacencia()` foi renomeado para indicar que é um método privado, seguindo boas práticas de programação.
*   A função `calcular_custo_total_solucao(solucao)` foi adicionada para facilitar a comparação entre soluções.
*   O código foi refatorado para melhorar a modularidade e facilitar a manutenção.

## Como Executar

**Etapa 3 (Solução Otimizada):**
Para executar o algoritmo completo (solução inicial + otimização):
1.  Certifique-se de ter Python instalado.
2.  Navegue até o diretório `Etapa3/`.
3.  Coloque as instâncias na pasta `MCGRP/`.
4.  Execute o script principal:
    ```bash
    python main.py
    ```
5.  Os arquivos de solução (`sol-*.dat`) serão gerados na pasta `G28/`.

## Dependências

*   Python 3.x

## Autores

*   Pedro Gonçalves Costa Melo
*   Lucas Henrique Lopes Costa
