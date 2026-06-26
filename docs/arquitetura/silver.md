# Silver

> Notebook: `03_bronze_to_silver.ipynb`

Aplica **Data Quality** sobre o Bronze e grava em Delta Lake no schema `silver`.

## Regras

- **Tipagem** — `cast` para os tipos corretos (int, double, date, string)
- **Padronização** — `trim`, `initcap` (nomes/cidade) e `lower` (email/status)
- **Deduplicação** — `dropDuplicates(["id"])`
- **Nulos** — remove registros com campos obrigatórios nulos
- **Validação** — `preco > 0`, `quantidade > 0`, `valor_total > 0`; `estoque` negativo vira `0`
- **Auditoria** — coluna `_silver_processed_at`

```python
clientes = (
    spark.table(f"{BRONZE_SCHEMA}.clientes")
        .select(
            col("id").cast("string").alias("id"),
            trim(initcap(col("nome"))).alias("nome"),
            trim(lower(col("email"))).alias("email"),
            trim(initcap(col("cidade"))).alias("cidade")
        )
        .dropDuplicates(["id"])
        .filter("id IS NOT NULL")
        .filter("nome IS NOT NULL")
        .filter("email IS NOT NULL")
        .withColumn("_silver_processed_at", current_timestamp())
)
```

Resultado: `silver.clientes`, `silver.produtos` e `silver.pedidos`.
