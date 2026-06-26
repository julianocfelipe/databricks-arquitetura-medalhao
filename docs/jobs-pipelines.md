# Jobs & Pipelines

O enunciado exige que **todas as execuções dos notebooks estejam encadeadas através de um Job
(Jobs & Pipelines)**, executado **sequencialmente**. Esta página documenta o Job criado no
Databricks.

## DAG do Job

O Job executa as 5 tasks em sequência — cada uma depende da anterior:

```
[001_Preparando_Ambiente]
            │
            ▼
[002_Landing_Extracao]
            │
            ▼
[003_Bronze_Ingestao]
            │
            ▼
[004_Silver_Data_Quality]
            │
            ▼
[005_Gold_Modelagem_Dimensional]
```

| Ordem | Task | Notebook | Depende de |
|-------|------|----------|------------|
| 1 | `preparar_ambiente` | `001_Preparando_Ambiente` | — |
| 2 | `landing` | `002_Landing_Extracao` | `preparar_ambiente` |
| 3 | `bronze` | `003_Bronze_Ingestao` | `landing` |
| 4 | `silver` | `004_Silver_Data_Quality` | `bronze` |
| 5 | `gold` | `005_Gold_Modelagem_Dimensional` | `silver` |

## Como criar o Job no Databricks

1. No menu lateral, vá em **Jobs & Pipelines → Create job**.
2. Dê um nome ao Job, ex.: `pipeline_medalhao_loja_virtual`.
3. **Task 1** — `preparar_ambiente`:
    - **Type:** Notebook
    - **Source:** Workspace → selecione `001_Preparando_Ambiente`
    - **Compute:** Serverless (padrão do Free Edition)
4. **Add task** — `landing`:
    - Notebook `002_Landing_Extracao`
    - **Depends on:** `preparar_ambiente`
5. Repita para `bronze` (002→003), `silver` (003→004) e `gold` (004→005), sempre definindo
   **Depends on** na task anterior, de modo que a execução seja **sequencial**.
6. **Run now** para executar o pipeline completo de ponta a ponta.

!!! tip "Free Edition é serverless"
    Não há cluster clássico para configurar — as tasks usam **compute serverless**. O driver do
    PostgreSQL é instalado dentro do notebook 002 via `%pip install psycopg2-binary`, então não há
    biblioteca Maven a instalar no cluster.

## Execução sequencial

Com as dependências configuradas, o Databricks garante a ordem
`001 → 002 → 003 → 004 → 005`. Se uma task falhar, as seguintes **não** são executadas,
preservando a integridade do pipeline Medalhão.

## Evidências da entrega

Anexe ao trabalho os prints do Databricks mostrando:

- A **lista de tasks** do Job com as dependências (DAG)
- Uma **execução concluída com sucesso** (todas as tasks verdes)
- As **tabelas criadas** nos schemas `bronze`, `silver` e `gold` (Catalog Explorer)
