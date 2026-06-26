# Bronze

> Notebook: `02_landing_to_bronze.ipynb`

Cópia das tabelas da Landing para **Delta Lake** (ACID, time travel), sem transformação de valores.

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

Resultado: `bronze.clientes`, `bronze.produtos` e `bronze.pedidos`.
