# Landing

> Notebook: `01_extract_supabase_to_landing.ipynb`

Primeira ingestão dos dados, no formato original da origem (CSV). O notebook também cria os schemas e
o Volume da Landing Zone.

## Etapas

1. Cria os schemas (`landing`, `bronze`, `silver`, `gold`) e o Volume `workspace.landing.dados`.
2. Lê as tabelas do Supabase via **JDBC**.
3. Grava cada tabela como CSV no Volume `/Volumes/workspace/landing/dados/{tabela}/`.
4. Registra as tabelas no schema `landing`.

```python
def read_supabase_table(table_name):
    return (
        spark.read
            .format("jdbc")
            .option("url", jdbc_url)
            .option("dbtable", f"public.{table_name}")
            .option("user", SUPABASE_USER)
            .option("password", SUPABASE_PASSWORD)
            .option("driver", "org.postgresql.Driver")
            .load()
    )
```

## Conexão (Session Pooler — IPv4)

```python
SUPABASE_HOST     = "aws-1-<regiao>.pooler.supabase.com"
SUPABASE_PORT     = "5432"
SUPABASE_DATABASE = "postgres"
SUPABASE_USER     = "postgres.<project-ref>"
SUPABASE_PASSWORD = "<senha>"
```

## Banco de origem (Supabase)

Execute o script abaixo no **SQL Editor** do Supabase para criar e popular as tabelas de origem.

```sql
DROP TABLE IF EXISTS pedidos  CASCADE;
DROP TABLE IF EXISTS produtos CASCADE;
DROP TABLE IF EXISTS clientes CASCADE;

CREATE TABLE clientes (
    id      INTEGER PRIMARY KEY,
    nome    VARCHAR(100) NOT NULL,
    email   VARCHAR(100) NOT NULL,
    cidade  VARCHAR(100)
);

CREATE TABLE produtos (
    id        INTEGER PRIMARY KEY,
    nome      VARCHAR(100) NOT NULL,
    categoria VARCHAR(100),
    preco     DECIMAL(10,2) NOT NULL,
    estoque   INTEGER DEFAULT 0
);

CREATE TABLE pedidos (
    id          INTEGER PRIMARY KEY,
    cliente_id  INTEGER NOT NULL REFERENCES clientes(id),
    produto_id  INTEGER NOT NULL REFERENCES produtos(id),
    quantidade  INTEGER NOT NULL,
    valor_total DECIMAL(10,2) NOT NULL,
    data_pedido DATE NOT NULL,
    status      VARCHAR(50) NOT NULL
);

INSERT INTO clientes (id, nome, email, cidade) VALUES
    (1, 'Ana Souza',    'ana@email.com',    'Florianopolis'),
    (2, 'Bruno Lima',   'bruno@email.com',  'Criciuma'),
    (3, 'Carla Mendes', 'carla@email.com',  'Joinville'),
    (4, 'Diego Ramos',  'diego@email.com',  'Blumenau'),
    (5, 'Elena Costa',  'elena@email.com',  'Chapeco');

INSERT INTO produtos (id, nome, categoria, preco, estoque) VALUES
    (1, 'Notebook Dell',    'Eletronicos', 3500.00, 50),
    (2, 'Mouse Logitech',   'Perifericos',   80.00, 200),
    (3, 'Teclado Mecanico', 'Perifericos',  150.00, 120),
    (4, 'Monitor 24pol',    'Eletronicos', 1200.00,  75),
    (5, 'Headset Gaming',   'Perifericos',  250.00,  90);

INSERT INTO pedidos (id, cliente_id, produto_id, quantidade, valor_total, data_pedido, status) VALUES
    (1, 1, 1, 1, 3500.00, '2024-01-10', 'entregue'),
    (2, 2, 2, 2,  160.00, '2024-01-12', 'entregue'),
    (3, 3, 3, 1,  150.00, '2024-01-15', 'em_transito'),
    (4, 4, 4, 1, 1200.00, '2024-01-18', 'processando'),
    (5, 5, 5, 2,  500.00, '2024-01-20', 'processando');
```
