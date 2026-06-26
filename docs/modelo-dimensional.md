# Modelo Dimensional

A camada **Gold** organiza os dados em um **Star Schema**: uma tabela **fato** central cercada por
**dimensões**.

```
        dim_cliente
             │
        fato_pedido ─── dim_produto
```

## Tabela fato

### `fato_pedido`

Registra cada pedido (transação de venda). Contém as **chaves de negócio** para as dimensões, as
**métricas** numéricas e os atributos de tempo derivados da data do pedido.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `pedido_id` | string | Chave de negócio do pedido |
| `cliente_id` | string | FK → `dim_cliente` |
| `produto_id` | string | FK → `dim_produto` |
| `data_pedido` | date | Data do pedido |
| `ano` / `mes` / `dia` | int | Atributos de tempo derivados |
| `quantidade` | int | Métrica — unidades |
| `valor_total` | double | Métrica — receita |
| `status` | string | Status do pedido |
| `gold_created_at` | timestamp | Auditoria |

## Dimensões

### `dim_cliente`

| Coluna | Descrição |
|--------|-----------|
| `cliente_id` | Chave de negócio |
| `nome_cliente` | Nome do cliente |
| `email` | E-mail |
| `cidade` | Cidade |

### `dim_produto`

| Coluna | Descrição |
|--------|-----------|
| `produto_id` | Chave de negócio |
| `nome_produto` | Nome do produto |
| `categoria` | Categoria |
| `preco` | Preço |

## Por que Star Schema?

- Consultas com `JOIN` simples entre a fato e as dimensões → ótimo desempenho de leitura
- Estrutura intuitiva para ferramentas de BI
- Separação clara entre **métricas** (fato) e **atributos descritivos** (dimensões)

## Exemplo de consulta

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
