
---

# 🚛 Análise e Modelagem de Grafos para Problemas de Logística

**Trabalho Prático Final**  
Disciplinas: GCC218 - Algoritmos em Grafos | GCC262 - Grafos e Suas Aplicações  
**Universidade Federal de Lavras (UFLA)**  
*Orientador: Prof. Mayron César O. Moreira*

---

## 📋 Introdução

Este projeto implementa a **Etapa 1** da modelagem de grafos para problemas logísticos, com:

- Representação de **multigrafos mistos** (arestas + arcos)
- Identificação de vértices/arestas/arcos com serviço requerido
- Cálculo de estatísticas estruturais e matrizes de caminhos mínimos

---

## 🛠️ Implementação

### Estrutura do Código

```bash
📦 ra-grafos-logistica/
├── grafo.py                 # Classe GrafoEtapa1 (leitura, análise e armazenamento)
├── visualizacao.ipynb       # Visualização com matplotlib
├── selected_instances/      # Arquivos de entrada (.bat)
└── README.md
```

### Funcionalidades Principais

1. **Classe `GrafoEtapa1`**:
   - `carregarDados()`: Processamento de arquivos `.bat`
   - `inicializarMatrizAdjacencia()`: Construção da matriz de custos
   - `calcularDistanciasMinimas()`: Implementação de Floyd-Warshall
   - `obterCaminhoMinimo()`: Recuperação de rotas ótimas

2. **Análise Descritiva**:
   - Cálculo de diâmetro, grau médio, densidade
   - Contagem de vértices/arestas/arcos (totais e requeridos)

3. **Visualização**:
   - Representação gráfica com `matplotlib`:
     - **Depósito**: Quadrado laranja
     - **Vértices requeridos**: Círculos pretos
     - **Arestas/arcos requeridos**: Linhas vermelhas

---

## 📥 Instalação

```bash
pip install matplotlib pandas
```

*Requisito: Python 3.10 ou superior*

## ⚠️ Observações Técnicas

1. **Restrições**:
   - Uso de bibliotecas como `networkx` ou `igraph` **não permitido**

2. **Dados de Entrada**:
   - Arquivos `.bat` devem ser obtidos no [repositório oficial](https://drive.google.com/file/d/1hlBu7L8OBqrwkVRRlFrVOTvBWKnqITxz/view?usp=drive_link)
   - Armazenamento na pasta `selected_instances/`

---

## 👥 Autores

- **Lucas Henrique Lopes Costa**  
- **Pedro Gonçalves Costa Melo**

---

## 📌 Considerações Finais

*Este trabalho é de natureza acadêmica. Qualquer utilização do código deve respeitar as normas de propriedade intelectual da UFLA.*

---
