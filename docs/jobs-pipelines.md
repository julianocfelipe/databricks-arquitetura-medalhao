# Jobs & Pipelines

O enunciado exige que **todas as execuções dos notebooks estejam encadeadas através de um Job
(Jobs & Pipelines)**, executado **sequencialmente**. Esta página documenta o Job criado no
Databricks.

## DAG do Job

O Job executa as 4 tasks do pipeline em sequência — cada uma depende da anterior:

```
[01_extract_supabase_to_landing]
            │
            ▼
[02_landing_to_bronze]
            │
            ▼
[03_bronze_to_silver]
            │
            ▼
[04_silver_to_gold]
```

| Ordem | Task | Notebook | Depende de |
|-------|------|----------|------------|
| 1 | `landing` | `01_extract_supabase_to_landing` | — |
| 2 | `bronze` | `02_landing_to_bronze` | `landing` |
| 3 | `silver` | `03_bronze_to_silver` | `bronze` |
| 4 | `gold` | `04_silver_to_gold` | `silver` |

> O `05_reset.ipynb` **não entra no Job** — é executado manualmente apenas quando se quer limpar o
> ambiente, para não apagar os dados a cada execução do pipeline.

## Como criar o Job no Databricks

1. No menu lateral, vá em **Jobs & Pipelines → Create job**.
2. Dê um nome ao Job, ex.: `pipeline_medalhao_loja_virtual`.
3. **Task 1** — `landing`:
    - **Type:** Notebook
    - **Source:** Workspace → selecione `01_extract_supabase_to_landing`
    - **Compute:** Serverless (padrão do Free Edition)
4. **Add task** — `bronze`:
    - Notebook `02_landing_to_bronze`
    - **Depends on:** `landing`
5. Repita para `silver` (03) e `gold` (04), sempre definindo **Depends on** na task anterior, de
   modo que a execução seja **sequencial**.
6. **Run now** para executar o pipeline completo de ponta a ponta.

!!! tip "Free Edition é serverless"
    Não há cluster clássico para configurar — as tasks usam **compute serverless**. O driver do
    PostgreSQL (`org.postgresql.Driver`) já vem no runtime, então não há biblioteca a instalar.

## Execução sequencial

Com as dependências configuradas, o Databricks garante a ordem `01 → 02 → 03 → 04`. Se uma task
falhar, as seguintes **não** são executadas, preservando a integridade do pipeline Medalhão.

## Evidências da entrega

Anexe ao trabalho os prints do Databricks mostrando:

- A **lista de tasks** do Job com as dependências (DAG)
- Uma **execução concluída com sucesso** (todas as tasks verdes)
- As **tabelas criadas** nos schemas `bronze`, `silver` e `gold` (Catalog Explorer)
