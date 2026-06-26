# Camada Gold

> Notebook: `005_Gold_Modelagem_Dimensional.py`

A **Gold** lê os dados do Silver e constrói o **modelo dimensional (Ralph Kimball)** — um
**Star Schema** otimizado para consumo analítico e BI. Formato **Delta Lake**, altamente governado.

## Star Schema

```
              dim_clientes
                   │
   dim_tempo ──── fato_pedidos ──── dim_produtos
```

| Tabela | Tipo | Chave (surrogate) |
|--------|------|-------------------|
| `dim_clientes` | Dimensão | `sk_cliente` |
| `dim_produtos` | Dimensão | `sk_produto` |
| `dim_tempo` | Dimensão | `sk_tempo` (`YYYYMMDD`) |
| `fato_pedidos` | Fato | `sk_pedido` |

> Detalhes do modelo na página **[Modelo Dimensional](../modelo-dimensional.md)**.

## Como é construído

1. **Dimensões** `dim_clientes` e `dim_produtos` — geram *surrogate key* com `row_number()`
   ordenado pelo id natural.
2. **`dim_tempo`** — gerada a partir das datas distintas dos pedidos; `sk_tempo` é o inteiro
   `YYYYMMDD`. Inclui ano, mês, dia, trimestre, nome do mês e dia da semana.
3. **`fato_pedidos`** — resolve as *surrogate keys* via `JOIN` com as dimensões e guarda as
   métricas (`quantidade_pedido`, `valor_total_pedido`, `status_pedido`).

```python
fato_pedidos = (
    df_silver_pedidos
    .join(df_dim_clientes.select("sk_cliente", "id_cliente"), on="id_cliente", how="left")
    .join(df_dim_produtos.select("sk_produto", "id_produto"), on="id_produto", how="left")
    .join(df_dim_tempo.select("sk_tempo", "data_completa"),
          df_silver_pedidos["data_pedido"] == df_dim_tempo["data_completa"], how="left")
    .withColumn("sk_pedido", F.row_number().over(Window.orderBy("id_pedido")))
)
```

## Análises de validação (Star Schema em ação)

O notebook executa consultas que comprovam o modelo:

- **Receita por categoria de produto** (`fato_pedidos` × `dim_produtos`)
- **Receita por cidade do cliente** (`fato_pedidos` × `dim_clientes`)
- **Pedidos por período** ano/mês (`fato_pedidos` × `dim_tempo`)

## Resultado

Schema `gold` com `dim_clientes`, `dim_produtos`, `dim_tempo` e `fato_pedidos` —
**pipeline Medalhão completo**: `Landing → Bronze → Silver → Gold`.
