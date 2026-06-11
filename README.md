# Pipeline de Dados - ETL Genérico

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED)

Pipeline ETL modular, extensível e reutilizável construído com boas práticas de engenharia de dados. Projeto pronto para servir como base para diferentes cenários de integração e processamento de dados.

## Arquitetura

```
├── config/                # Configurações YAML do pipeline
├── data/
│   ├── raw/              # Dados brutos (input)
│   ├── processed/        # Dados intermediários
│   └── output/           # Dados processados (output)
├── logs/                 # Logs de execução
├── notebooks/            # Análises exploratórias
├── scripts/
│   └── run_pipeline.py   # Entrypoint de execução
├── src/
│   ├── connectors/       # Conectores (CSV, API, SQL)
│   ├── pipeline/         # Core ETL (extract, transform, load)
│   ├── quality/          # Data quality checks
│   └── utils/            # Utilitários (logger, database, validators)
└── tests/                # Testes unitários
```

## Funcionalidades

- **Extração** de CSV, API REST e bancos SQL
- **Transformações** modulares: limpeza, remoção de duplicatas, conversão de tipos, filtros, renomeação e metadados
- **Carga** em CSV ou banco SQL
- **Quality checks** configuráveis: nulos, duplicatas, ranges, schema
- **Logging** estruturado com rotação de arquivos
- **Orquestração** com retry, timeout e relatório de execução
- **Agendamento** integrado (daily, hourly, weekly)
- **Docker** pronto para execução conteinerizada
- **Testes** unitários com pytest
- **Configuração** via YAML flexível

## Quick Start

```bash
# Instalar dependências
make install

# Executar pipeline
make run

# Com relatório JSON
make run-json
```

## Configuração

Edite `config/config.yaml` para definir:

- **Fonte de dados**: CSV, API ou SQL
- **Etapas de transformação**: ligue/desligue cada etapa
- **Quality checks**: thresholds e regras de validação
- **Destino dos dados**: CSV ou banco SQL

## Docker

```bash
# Build da imagem
make docker-build

# Executar pipeline
make docker-run

# Agendar execução diária
make docker-run-scheduled
```

## Testes

```bash
# Todos os testes com cobertura
make test

# Apenas testes rápidos
make test-simple
```

## Exemplos de Uso

### Extrair de CSV, transformar e salvar

```yaml
# config/config.yaml
extract:
  source: csv
  csv:
    path: "data/raw/vendas.csv"

transform:
  steps:
    - name: clean_missing_values
      strategy: drop
    - name: remove_duplicates
    - name: add_metadata

load:
  target: csv
  csv:
    path: "data/output/vendas_processadas.csv"
```

### Extrair de API com paginação

```yaml
extract:
  source: api
  api:
    url: "https://api.exemplo.com/v1/dados"
    method: GET
    pagination:
      enabled: true
      page_size: 100
      max_pages: 5
```
