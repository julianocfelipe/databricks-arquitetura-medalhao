# Camada Silver

> Notebook: `03_bronze_to_silver.ipynb`

A **Silver** lê os dados do Bronze, aplica **regras de Data Quality** e padronização, e grava em
formato **Delta Lake** no schema `silver`.

## Regras de Data Quality aplicadas

| Regra | Descrição |
|-------|-----------|
| Tipagem | Converte os campos para os tipos corretos (`cast` para int, double, date, string) |
| Strings | `trim` + normalização (`initcap` para nomes/cidade, `lower` para email/status) |
| Deduplicação | Remove registros com chave primária duplicada (`dropDuplicates(["id"])`) |
| Nulos | Filtra registros com campos obrigatórios nulos |
| Validação | Remove valores inválidos (`preco > 0`, `quantidade > 0`, `valor_total > 0`) |
| Normalização | `estoque` negativo é ajustado para `0` |
| Metadados | Adiciona `_silver_processed_at` |

## Exemplos por tabela

### Clientes
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

### Produtos
- `preco` convertido para `double` e filtrado (`preco > 0`)
- `estoque` convertido para `int`; valores negativos viram `0`
- `nome` e `categoria` padronizados com `trim` + `initcap`

### Pedidos
- `quantidade` (int) e `valor_total` (double) validados (`> 0`)
- `data_pedido` convertida para `date`
- `status` normalizado com `lower` + `trim`

## Resultado

Tabelas `silver.clientes`, `silver.produtos` e `silver.pedidos` — dados limpos, validados e
padronizados, prontos para alimentar o modelo dimensional na camada **Gold**.
