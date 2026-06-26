# Camada Silver

> Notebook: `004_Silver_Data_Quality.py`

A **Silver** lê os dados do Bronze, aplica **regras de Data Quality** e padronização, e grava em
formato **Delta Lake** no schema `silver`. É a camada usada por engenheiros de dados e de ML/IA
para consultas *ad hoc*.

## Regras de Data Quality aplicadas

| Regra | Descrição |
|-------|-----------|
| Deduplicação | Remove registros com chave primária duplicada (`dropDuplicates`) |
| Nulos | Filtra registros com campos obrigatórios nulos |
| Tipos | Garante tipos corretos (data, decimal, inteiro) |
| Strings | `trim` e normalização de capitalização (`initcap` / `lower`) |
| Validação | Remove valores inválidos (preço ≤ 0, quantidade ≤ 0, etc.) |
| Renomeação | Colunas em `snake_case` sem abreviações (ex.: `id` → `id_cliente`) |
| Metadados | Atualiza `data_processamento` e descarta `nome_arquivo` do bronze |

## Exemplos por tabela

### Clientes
- Dedup por `id`; remove nulos em `id`, `nome`, `email`
- `nome` → `initcap(trim(...))`, `email` → `lower(trim(...))`
- `cidade` nula vira `"Nao Informado"`
- Renomeia para `id_cliente`, `nome_cliente`, `email_cliente`, `cidade_cliente`

### Produtos
- Remove produtos com `preco` nulo ou ≤ 0
- `estoque` nulo/negativo é normalizado para `0`
- `preco` arredondado para 2 casas
- Renomeia para `id_produto`, `nome_produto`, `categoria_produto`, `preco_produto`, `estoque_produto`

### Pedidos
- Remove pedidos com `valor_total` ou `quantidade` inválidos (nulos ou ≤ 0)
- `status` normalizado; valores fora do domínio viram `"desconhecido"`
  (domínio: `entregue`, `em_transito`, `processando`, `finalizado`, `cancelado`)
- `data_pedido` convertida para `date`
- Renomeia para `id_pedido`, `id_cliente`, `id_produto`, `quantidade_pedido`,
  `valor_total_pedido`, `status_pedido`

```python
df_clientes_silver = (
    df_clientes_bronze
    .dropDuplicates(["id"])
    .filter(F.col("id").isNotNull())
    .withColumn("nome",  F.initcap(F.trim(F.col("nome"))))
    .withColumn("email", F.lower(F.trim(F.col("email"))))
    .withColumnRenamed("id", "id_cliente")
    .withColumn("data_processamento", F.current_timestamp())
    .drop("nome_arquivo")
)
```

## Resultado

Tabelas `silver.clientes`, `silver.produtos` e `silver.pedidos` — dados limpos, validados e
padronizados, prontos para alimentar o modelo dimensional na camada **Gold**.
