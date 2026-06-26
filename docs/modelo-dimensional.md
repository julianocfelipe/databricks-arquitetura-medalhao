# Modelo Dimensional

Star Schema da camada Gold: uma fato central cercada por dimensões.

```mermaid
erDiagram
    dim_cliente ||--o{ fato_pedido : "cliente_id"
    dim_produto ||--o{ fato_pedido : "produto_id"

    dim_cliente {
        string cliente_id PK
        string nome_cliente
        string email
        string cidade
        timestamp gold_created_at
    }

    dim_produto {
        string produto_id PK
        string nome_produto
        string categoria
        double preco
        timestamp gold_created_at
    }

    fato_pedido {
        string pedido_id PK
        string cliente_id FK
        string produto_id FK
        date data_pedido
        int ano
        int mes
        int dia
        int quantidade
        double valor_total
        string status
        timestamp gold_created_at
    }
```

## `fato_pedido`

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `pedido_id` | string | Chave do pedido |
| `cliente_id` | string | FK → `dim_cliente` |
| `produto_id` | string | FK → `dim_produto` |
| `data_pedido` | date | Data do pedido |
| `ano` / `mes` / `dia` | int | Atributos de tempo |
| `quantidade` | int | Métrica |
| `valor_total` | double | Métrica |
| `status` | string | Status do pedido |
| `gold_created_at` | timestamp | Auditoria |

## `dim_cliente`

| Coluna | Descrição |
|--------|-----------|
| `cliente_id` | Chave do cliente |
| `nome_cliente` | Nome |
| `email` | E-mail |
| `cidade` | Cidade |

## `dim_produto`

| Coluna | Descrição |
|--------|-----------|
| `produto_id` | Chave do produto |
| `nome_produto` | Nome |
| `categoria` | Categoria |
| `preco` | Preço |

## Consulta de exemplo

```sql
SELECT
    c.cidade,
    COUNT(f.pedido_id) AS total_pedidos,
    SUM(f.valor_total) AS receita_total
FROM workspace.gold.fato_pedido f
JOIN workspace.gold.dim_cliente c ON f.cliente_id = c.cliente_id
GROUP BY c.cidade
ORDER BY receita_total DESC;
```
