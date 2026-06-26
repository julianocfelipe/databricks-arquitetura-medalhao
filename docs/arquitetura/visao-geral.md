# Visão Geral da Arquitetura Medalhão

A **Arquitetura Medalhão** (também chamada de *multi-hop*) é um padrão de design de dados usado para
organizar logicamente os dados de um **Data Lakehouse**. O objetivo é **melhorar de forma incremental e
progressiva** a estrutura e a qualidade dos dados à medida que eles fluem pelas camadas.

Neste trabalho, o pipeline tem **quatro camadas** (Landing → Bronze → Silver → Gold), todas executadas
no **Databricks Free Edition** (serverless) e encadeadas por um **Job (Jobs & Pipelines)**.

## Fluxo do pipeline

```
Supabase (PostgreSQL)
        │  JDBC
        ▼
   LANDING              CSV brutos (formato original da origem)
        │
        ▼
     BRONZE             cópia em Delta Lake
        │
        ▼
     SILVER             Delta Lake + Data Quality
        │
        ▼
      GOLD              Delta Lake + Star Schema
```

## Resumo das camadas

| Camada | Formato | Conteúdo | Notebook |
|--------|---------|----------|----------|
| **Landing** | CSV | Cópia bruta da origem (Volume), camada provisória de ingestão | `01_extract_supabase_to_landing.ipynb` |
| **Bronze** | Delta Lake | Cópia das tabelas da Landing em Delta | `02_landing_to_bronze.ipynb` |
| **Silver** | Delta Lake | Dados limpos, padronizados e validados (Data Quality) | `03_bronze_to_silver.ipynb` |
| **Gold** | Delta Lake | Modelo dimensional (star schema) para consumo/BI | `04_silver_to_gold.ipynb` |

> O notebook `05_reset.ipynb` não faz parte do fluxo — serve para **limpar o ambiente** (remover
> tabelas e zerar o Volume) quando for preciso recomeçar.

## Característica de cada camada

- **Landing** — camada provisória da primeira ingestão. Formato original da origem (CSV). Aqui também
  são criados os schemas (`landing`, `bronze`, `silver`, `gold`) e o **Volume** da Landing Zone.
- **Bronze** — cópia da landing em **Delta Lake** (ACID, metadados). Mantém o histórico dos dados brutos.
- **Silver** — formato Delta. Aplica **regras de qualidade e padronização** (trim, maiúsculo/minúsculo,
  tipagem), remove duplicados e registros inválidos.
- **Gold** — formato Delta. Dados em **modelo dimensional (star schema)**, otimizado para leitura e BI.

## Onde o ambiente é preparado

A criação dos schemas e do Volume acontece **no início do notebook `01_extract_supabase_to_landing.ipynb`**
(via `%sql`), antes da extração — por isso o pipeline tem 5 notebooks (sem um notebook separado só de setup).
