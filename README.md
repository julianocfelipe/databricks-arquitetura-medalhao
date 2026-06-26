# Trabalho 3 — Databricks: Arquitetura Medalhão

Pipeline de dados no **Databricks Free Edition** implementando a **Arquitetura Medalhão** (Landing → Bronze → Silver → Gold) com Jobs & Pipelines.

## Contexto

Este trabalho é um complemento dos trabalhos 1 e 2, migrando o mesmo dataset (Loja Virtual) para uma solução **PaaS na nuvem** com Databricks.

| Trabalho | Tecnologias | Foco |
|----------|-------------|------|
| 1 | Apache Spark + Delta Lake (local) | Delta Lake e DML |
| 2 | SQL Server + MinIO + Spark (Docker) | Ingestão Landing → Bronze |
| **3** | **Databricks + Supabase** | **Pipeline completo Medalhão** |

## Arquitetura

```
Supabase (PostgreSQL)
       │
       ▼
  LANDING               ← CSV bruto extraído via JDBC (Volume do Unity Catalog)
       │
       ▼
    BRONZE              ← cópia em Delta Lake
       │
       ▼
    SILVER              ← Delta Lake + Data Quality
       │
       ▼
     GOLD               ← Delta Lake + Star Schema (modelagem dimensional)
```

## Modelo de dados

### Origem (Supabase)
- `clientes` (id, nome, email, cidade)
- `produtos` (id, nome, categoria, preco, estoque)
- `pedidos` (id, cliente_id, produto_id, quantidade, valor_total, data_pedido, status)

### Gold — Star Schema
```
        dim_cliente
             │
        fato_pedido ─── dim_produto
```

| Tabela | Tipo | Chave de negócio |
|--------|------|------------------|
| `dim_cliente` | Dimensão | cliente_id |
| `dim_produto` | Dimensão | produto_id |
| `fato_pedido` | Fato | pedido_id |

> A fato `fato_pedido` guarda as métricas (`quantidade`, `valor_total`), o `status` e os atributos de
> tempo derivados da data do pedido (`ano`, `mes`, `dia`).

## Notebooks

| Notebook | Etapa | Descrição |
|----------|-------|-----------|
| `01_extract_supabase_to_landing.ipynb` | Landing | Cria schemas/Volume e extrai do Supabase (JDBC) → CSV + tabelas na Landing |
| `02_landing_to_bronze.ipynb` | Bronze | Landing → Delta Lake (Bronze) |
| `03_bronze_to_silver.ipynb` | Silver | Data Quality + padronização |
| `04_silver_to_gold.ipynb` | Gold | Modelagem dimensional (star schema) |
| `05_reset.ipynb` | Reset | Remove as tabelas e limpa o Volume para recomeçar |

## Tecnologias

- [Databricks Free Edition](https://www.databricks.com/learn/free-edition)
- [Supabase](https://supabase.com) — PostgreSQL cloud (banco de origem)
- Delta Lake — formato de armazenamento
- Apache Spark (PySpark) — processamento
- Jobs & Pipelines — orquestração

## Como executar

### Pré-requisitos
1. Conta no [Databricks Free Edition](https://www.databricks.com/learn/free-edition) (serverless)
2. Conta no [Supabase](https://supabase.com)

> O Free Edition é serverless. A leitura do PostgreSQL usa **JDBC** (`org.postgresql.Driver`), que já
> vem incluído no Databricks Runtime — **não é preciso instalar bibliotecas** (nem Maven nem pip).

### Passo a passo
1. Crie o banco de origem no Supabase executando o script SQL disponível na
   [documentação — Landing](https://julianocfelipe.github.io/databricks-arquitetura-medalhao/arquitetura/landing/)
2. Importe os notebooks da pasta `notebooks/` no workspace do Databricks
3. Configure as credenciais do Supabase (Session Pooler) no notebook `01_extract_supabase_to_landing.ipynb`
4. Execute os notebooks na ordem (01 → 02 → 03 → 04)
5. Ou execute o **Job** (Jobs & Pipelines) com as 4 tasks encadeadas para automação completa
6. Use o `05_reset.ipynb` quando quiser limpar o ambiente e recomeçar

## Estrutura do repositório

```
├── notebooks/               # Notebooks Databricks (.ipynb)
│   ├── 01_extract_supabase_to_landing.ipynb
│   ├── 02_landing_to_bronze.ipynb
│   ├── 03_bronze_to_silver.ipynb
│   ├── 04_silver_to_gold.ipynb
│   └── 05_reset.ipynb
├── docs/                    # Documentação (MkDocs)
├── site/                    # Site gerado pelo MkDocs (gh-pages)
├── mkdocs.yml               # Configuração do MkDocs
└── README.md
```

## Documentação

Consulte a [documentação completa](https://julianocfelipe.github.io/databricks-arquitetura-medalhao/) para detalhes da arquitetura, setup do Supabase, modelo dimensional e o Job de orquestração.
