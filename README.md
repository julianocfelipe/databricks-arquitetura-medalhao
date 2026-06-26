# Trabalho 3 — Lakehouse com Databricks e Arquitetura Medalhão

Pipeline de dados no **Databricks Free Edition** que implementa a **Arquitetura Medalhão**
(Landing → Bronze → Silver → Gold), extraindo um banco PostgreSQL hospedado no **Supabase** e
orquestrando as etapas via **Jobs & Pipelines**.

## Arquitetura

```
Supabase (PostgreSQL)
       │  JDBC
       ▼
   LANDING    CSV bruto em Volume do Unity Catalog
       ▼
   BRONZE     cópia em Delta Lake
       ▼
   SILVER     Delta Lake + Data Quality
       ▼
    GOLD      Star Schema (modelo dimensional)
```

## Modelo de dados

**Origem (Supabase)**

- `clientes` (id, nome, email, cidade)
- `produtos` (id, nome, categoria, preco, estoque)
- `pedidos` (id, cliente_id, produto_id, quantidade, valor_total, data_pedido, status)

**Gold — Star Schema**

```
    dim_cliente
         │
    fato_pedido ─── dim_produto
```

| Tabela | Tipo | Chave |
|--------|------|-------|
| `dim_cliente` | Dimensão | `cliente_id` |
| `dim_produto` | Dimensão | `produto_id` |
| `fato_pedido` | Fato | `pedido_id` |

## Notebooks

| Notebook | Camada |
|----------|--------|
| `01_extract_supabase_to_landing.ipynb` | Landing — cria schemas/Volume e extrai do Supabase via JDBC |
| `02_landing_to_bronze.ipynb` | Bronze — ingestão em Delta Lake |
| `03_bronze_to_silver.ipynb` | Silver — Data Quality e padronização |
| `04_silver_to_gold.ipynb` | Gold — modelagem dimensional |
| `05_reset.ipynb` | Utilitário — limpa o ambiente |

## Tecnologias

![Databricks](https://img.shields.io/badge/Databricks-Free_Edition-FF3621?logo=databricks&logoColor=white)
![Apache Spark](https://img.shields.io/badge/Apache_Spark-PySpark-E25A1C?logo=apachespark&logoColor=white)
![Delta Lake](https://img.shields.io/badge/Delta_Lake-Lakehouse-00ADD4?logo=delta&logoColor=white)
![Unity Catalog](https://img.shields.io/badge/Unity_Catalog-Volumes-FF3621?logo=databricks&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-JDBC-4169E1?logo=postgresql&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3FCF8E?logo=supabase&logoColor=white)
![Python](https://img.shields.io/badge/Python-3-3776AB?logo=python&logoColor=white)
![MkDocs](https://img.shields.io/badge/MkDocs-Material-526CFE?logo=materialformkdocs&logoColor=white)

## Como executar

1. No Supabase, crie o banco de origem com o script SQL da [documentação](https://julianocfelipe.github.io/databricks-arquitetura-medalhao/arquitetura/landing/).
2. Importe os notebooks de `notebooks/` no workspace do Databricks.
3. Em `01_extract_supabase_to_landing.ipynb`, configure as credenciais do Session Pooler do Supabase.
4. Execute os notebooks na ordem `01 → 02 → 03 → 04`, ou crie um **Job** com as 4 tasks encadeadas.
5. Use `05_reset.ipynb` para limpar o ambiente quando necessário.

## Estrutura

```
├── notebooks/     # Notebooks Databricks (.ipynb)
├── docs/          # Documentação (MkDocs)
├── mkdocs.yml
└── README.md
```

## Documentação

Disponível em **https://julianocfelipe.github.io/databricks-arquitetura-medalhao/**.

## Referências

- [Databricks Documentation](https://docs.databricks.com/)
- [Apache Spark — PySpark](https://spark.apache.org/docs/latest/api/python/index.html)
- [Delta Lake](https://docs.delta.io/latest/index.html)
- [Unity Catalog — Volumes](https://docs.databricks.com/aws/en/volumes/)
- [PostgreSQL JDBC Driver](https://jdbc.postgresql.org/documentation/)
- [Supabase — Connecting to Postgres](https://supabase.com/docs/guides/database/connecting-to-postgres)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [Claude (Anthropic)](https://www.anthropic.com/claude) — assistente de IA usado no desenvolvimento
