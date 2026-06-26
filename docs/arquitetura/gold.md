# Camada Gold

> Notebook: `04_silver_to_gold.ipynb`

A **Gold** lê os dados do Silver e constrói o **modelo dimensional** — um **Star Schema** otimizado
para consumo analítico e BI. Formato **Delta Lake**.

## Star Schema

```
        dim_cliente
             │
        fato_pedido ─── dim_produto
```

| Tabela | Tipo | Chave de negócio |
|--------|------|------------------|
| `dim_cliente` | Dimensão | `cliente_id` |
| `dim_produto` | Dimensão | `produto_id` |
| `fato_pedido` | Fato | `pedido_id` |

> Detalhes do modelo na página **[Modelo Dimensional](../modelo-dimensional.md)**.

## Como é construído

1. **`dim_cliente`** e **`dim_produto`** — selecionam os atributos descritivos do Silver e renomeiam a
   chave de negócio (`id` → `cliente_id` / `produto_id`).
2. **`fato_pedido`** — parte da tabela `silver.pedidos`, mantém as chaves de negócio (`cliente_id`,
   `produto_id`), as métricas (`quantidade`, `valor_total`), o `status` e deriva atributos de tempo
   (`ano`, `mes`, `dia`) a partir de `data_pedido`.

```python
fato_pedido = (
    pedidos
        .select(
            col("id").alias("pedido_id"),
            col("cliente_id"),
            col("produto_id"),
            col("data_pedido"),
            year(col("data_pedido")).alias("ano"),
            month(col("data_pedido")).alias("mes"),
            dayofmonth(col("data_pedido")).alias("dia"),
            col("quantidade"),
            col("valor_total"),
            col("status"),
            current_timestamp().alias("gold_created_at")
        )
)
```

## Exemplo de consulta (Star Schema em ação)

```sql
SELECT
    p.categoria,
    COUNT(f.pedido_id)   AS total_pedidos,
    SUM(f.valor_total)   AS receita_total
FROM workspace.gold.fato_pedido f
JOIN workspace.gold.dim_produto p ON f.produto_id = p.produto_id
GROUP BY p.categoria
ORDER BY receita_total DESC;
```

## Resultado

Schema `gold` com `dim_cliente`, `dim_produto` e `fato_pedido` —
**pipeline Medalhão completo**: `Landing → Bronze → Silver → Gold`.
