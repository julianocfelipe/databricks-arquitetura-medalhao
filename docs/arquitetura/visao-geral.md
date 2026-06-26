# Visão Geral da Arquitetura Medalhão

A **Arquitetura Medalhão** (também chamada de *multi-hop*) é um padrão de design de dados usado para
organizar logicamente os dados de um **Data Lakehouse**. O objetivo é **melhorar de forma incremental e
progressiva** a estrutura e a qualidade dos dados à medida que eles fluem pelas camadas.

Neste trabalho, o pipeline tem **quatro camadas** (Landing → Bronze → Silver → Gold), todas executadas
no **Databricks Free Edition** e encadeadas por um **Job (Jobs & Pipelines)**.

## Fluxo do pipeline

```
Supabase (PostgreSQL)
        │  JDBC
        ▼
   LANDING / DADOS      CSV brutos (formato original da origem)
        │
        ▼
     BRONZE             Delta Lake + metadados de auditoria
        │
        ▼
     SILVER             Delta Lake + Data Quality
        │
        ▼
      GOLD              Delta Lake + Star Schema (Ralph Kimball)
```

## Resumo das camadas

| Camada | Formato | Conteúdo | Notebook |
|--------|---------|----------|----------|
| **Landing** | CSV | Cópia bruta da origem, camada provisória de ingestão | `002_Landing_Extracao.ipynb` |
| **Bronze** | Delta Lake | Histórico completo dos dados brutos + metadados | `003_Bronze_Ingestao.ipynb` |
| **Silver** | Delta Lake | Dados limpos, padronizados e validados (Data Quality) | `004_Silver_Data_Quality.ipynb` |
| **Gold** | Delta Lake | Modelo dimensional (Kimball) otimizado para consumo/BI | `005_Gold_Modelagem_Dimensional.ipynb` |

## Característica de cada camada

- **Landing** — camada provisória da primeira ingestão. Formato original da origem (CSV/JSON). Usada
  apenas por engenheiros de dados, normalmente como backup para recriar conjuntos de dados.
- **Bronze** — cópia da landing, mas em **Delta Lake** (ACID, metadados). Mantém o histórico completo,
  dados imutáveis (apenas leitura), normalmente particionados por data.
- **Silver** — formato Delta. Aplica **regras de qualidade e padronização** (nomenclatura, maiúsculo
  x minúsculo, remoção de abreviações), remove duplicados, trata nulos e valores inválidos.
- **Gold** — formato Delta. Dados transformados segundo as **regras de negócio**, em modelo otimizado
  para leitura (dimensional / star schema). Altamente governado e documentado.

## Setup do ambiente (notebook 001)

O notebook `001_Preparando_Ambiente.ipynb` prepara todo o ambiente antes da execução:

- Remove o ambiente anterior (execução limpa)
- Cria os schemas `landing`, `bronze`, `silver` e `gold`
- Cria a Landing Zone como **Volume** do Unity Catalog (`/Volumes/<catalog>/landing/dados`)

Veja os detalhes de cada etapa nas páginas seguintes.
