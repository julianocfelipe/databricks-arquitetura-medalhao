# Trabalho 3 — Databricks: Arquitetura Medalhão

Pipeline de dados completo no **Databricks Free Edition** implementando a **Arquitetura Medalhão**,
com orquestração via **Jobs & Pipelines**.

## Objetivo

Construir um pipeline de dados (**Landing → Bronze → Silver → Gold**) utilizando o mesmo dataset da
Loja Virtual dos trabalhos anteriores, agora em uma solução **PaaS na nuvem**.

## Pipeline

```
Supabase (PostgreSQL)
        │  JDBC
        ▼
   LANDING / DADOS    CSV brutos
        │
        ▼
     BRONZE           Delta Lake + metadados
        │
        ▼
     SILVER           Delta Lake + Data Quality
        │
        ▼
      GOLD            Delta Lake + Star Schema
```

## Navegação

- **[Visão Geral](arquitetura/visao-geral.md)** — conceitos da arquitetura e resumo das camadas
- **[Landing](arquitetura/landing.md)** — extração da origem + setup do Supabase
- **[Bronze](arquitetura/bronze.md)** — ingestão em Delta Lake
- **[Silver](arquitetura/silver.md)** — Data Quality e padronização
- **[Gold](arquitetura/gold.md)** — modelagem dimensional
- **[Modelo Dimensional](modelo-dimensional.md)** — detalhes do Star Schema
- **[Jobs & Pipelines](jobs-pipelines.md)** — orquestração sequencial dos notebooks

## Tecnologias

- **Databricks Free Edition** — plataforma de processamento
- **Supabase** — banco PostgreSQL na nuvem (origem)
- **Delta Lake** — formato de armazenamento ACID
- **Apache Spark (PySpark)** — processamento distribuído
- **Jobs & Pipelines** — orquestração sequencial

## Screenshots

> Adicione aqui prints do Databricks mostrando:
>
> - Execução dos notebooks
> - DAG do Job (Jobs & Pipelines)
> - Tabelas criadas no Catalog Explorer
> - Resultados das queries no Gold
