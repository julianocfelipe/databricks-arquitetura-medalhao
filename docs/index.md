# Trabalho 3 — Databricks: Arquitetura Medalhão

Pipeline de dados completo no **Databricks Free Edition** implementando a **Arquitetura Medalhão**.

## Objetivo

Construir um pipeline de dados (Landing → Bronze → Silver → Gold) com orquestração via **Jobs & Pipelines**, utilizando o mesmo dataset da Loja Virtual dos trabalhos anteriores.

## Pipeline

```
Supabase (PostgreSQL)
        │  JDBC
        ▼
   LANDING/DADOS     CSV brutos
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

## Screenshots

> Adicione aqui screenshots do Databricks mostrando:
> - Execução dos notebooks
> - DAG do Job
> - Tabelas criadas no Catalog Explorer
> - Resultados das queries no Gold

## Tecnologias

- **Databricks Free Edition** — plataforma de processamento
- **Supabase** — banco de dados PostgreSQL na nuvem (origem)
- **Delta Lake** — formato de armazenamento ACID
- **Apache Spark (PySpark)** — processamento distribuído
- **Jobs & Pipelines** — orquestração sequencial
