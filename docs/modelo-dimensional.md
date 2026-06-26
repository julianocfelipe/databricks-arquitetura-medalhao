# Modelo Dimensional (Ralph Kimball)

A camada **Gold** organiza os dados em um **Star Schema** segundo a metodologia de **Ralph Kimball**:
uma tabela **fato** central cercada por **dimensões**.

```
              dim_clientes
                   │
   dim_tempo ──── fato_pedidos ──── dim_produtos
```

## Tabela fato

### `fato_pedidos`

Registra cada transação de venda. Contém as **chaves estrangeiras** (surrogate keys) para as
dimensões e as **métricas** numéricas.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `sk_pedido` | int | Surrogate key da fato |
| `id_pedido` | int | Chave natural do pedido |
| `sk_cliente` | int | FK → `dim_clientes` |
| `sk_produto` | int | FK → `dim_produtos` |
| `sk_tempo` | int | FK → `dim_tempo` (`YYYYMMDD`) |
| `quantidade_pedido` | int | Métrica — unidades |
| `valor_total_pedido` | double | Métrica — receita |
| `status_pedido` | string | Status do pedido |
| `data_processamento` | timestamp | Auditoria |

## Dimensões

### `dim_clientes`

| Coluna | Descrição |
|--------|-----------|
| `sk_cliente` | Surrogate key |
| `id_cliente` | Chave natural |
| `nome_cliente`, `email_cliente`, `cidade_cliente` | Atributos descritivos |

### `dim_produtos`

| Coluna | Descrição |
|--------|-----------|
| `sk_produto` | Surrogate key |
| `id_produto` | Chave natural |
| `nome_produto`, `categoria_produto`, `preco_produto` | Atributos descritivos |

### `dim_tempo`

| Coluna | Descrição |
|--------|-----------|
| `sk_tempo` | Surrogate key (`YYYYMMDD`) |
| `data_completa` | Data |
| `ano`, `mes`, `dia`, `trimestre` | Partes da data |
| `nome_mes`, `dia_semana` | Atributos descritivos |

## Por que Star Schema?

- **Surrogate keys** desacoplam o modelo analítico das chaves do sistema de origem
- Consultas com `JOIN` simples entre fato e dimensões → ótimo desempenho de leitura
- Estrutura intuitiva para ferramentas de BI

## Exemplo de consulta

```sql
SELECT
    p.categoria_produto,
    COUNT(f.id_pedido)        AS total_pedidos,
    SUM(f.valor_total_pedido) AS receita_total
FROM gold.fato_pedidos f
JOIN gold.dim_produtos  p ON f.sk_produto = p.sk_produto
GROUP BY p.categoria_produto
ORDER BY receita_total DESC;
```
