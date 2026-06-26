# Camada Bronze

> Notebook: `02_landing_to_bronze.ipynb`

A **Bronze** é a cópia das tabelas da camada Landing, agora em **Delta Lake** (ACID, metadados,
time travel). Mantém os dados brutos, sem transformação de valores.

## O que a camada faz

- Lê as tabelas do schema `landing` (`workspace.landing.{tabela}`)
- Grava cada uma como **tabela Delta gerenciada** no schema `bronze`

```python
for table in TABLES:
    df = spark.table(f"{LANDING_SCHEMA}.{table}")

    (
        df.write
            .format("delta")
            .mode("overwrite")
            .saveAsTable(f"{BRONZE_SCHEMA}.{table}")
    )
```

## Características

- **Formato Delta** (ACID, metadados, time travel)
- Cópia fiel da landing, sem transformação de valores
- Já carrega os metadados de auditoria adicionados na Landing (`_source_table`, `_extracted_at`)

## Validações do notebook

- `SHOW TABLES IN workspace.bronze`
- `spark.table("workspace.bronze.clientes").show()`
- `DESCRIBE DETAIL workspace.bronze.clientes`

## Resultado

Tabelas Delta `bronze.clientes`, `bronze.produtos` e `bronze.pedidos`, prontas para receber as
regras de **Data Quality** na camada Silver.
