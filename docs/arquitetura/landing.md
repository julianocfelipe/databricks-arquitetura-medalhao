# Camada Landing

> Notebook: `01_extract_supabase_to_landing.ipynb`

A **Landing** é a camada provisória responsável pela **primeira ingestão** dos dados no Data Lake.
Os dados são gravados no **formato original da origem** — neste trabalho, **CSV** (origem relacional).

Este notebook também **prepara o ambiente**: cria os schemas (`landing`, `bronze`, `silver`, `gold`)
e o **Volume** da Landing Zone.

```sql
CREATE SCHEMA IF NOT EXISTS landing;
CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

CREATE VOLUME IF NOT EXISTS workspace.landing.dados;
```

## O que a camada faz

- Conecta no banco de origem (**Supabase / PostgreSQL**) via **JDBC**
- Extrai **todas as tabelas** (`clientes`, `produtos`, `pedidos`)
- Adiciona metadados de auditoria (`_source_table`, `_extracted_at`)
- Grava cada tabela como **CSV** no Volume `/Volumes/workspace/landing/dados/{tabela}/`
- Registra as tabelas no schema `landing`

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

!!! info "Databricks Free Edition é serverless"
    O driver JDBC do PostgreSQL (`org.postgresql.Driver`) **já vem incluído no Databricks Runtime**,
    então **não é preciso instalar nada** (nem biblioteca Maven nem `pip`). A Landing Zone usa um
    **Volume** do Unity Catalog (`/Volumes/workspace/landing/dados`), e não o DBFS `/FileStore`
    (restrito no serverless).

!!! warning "Conexão: use o Session Pooler (IPv4)"
    A conexão **direta** (`db.xxxx.supabase.co`) costuma ser apenas IPv6 e não é alcançável pelo
    Databricks serverless. Use os dados do **Session Pooler** (IPv4, porta `5432`):
    host `aws-1-<regiao>.pooler.supabase.com` e usuário `postgres.<project-ref>`.

## Configuração da conexão

No início do notebook, preencha as credenciais do **Session Pooler** do seu projeto Supabase
(em **Connect → Session pooler**):

```python
SUPABASE_HOST     = "aws-1-<regiao>.pooler.supabase.com"
SUPABASE_PORT     = "5432"
SUPABASE_DATABASE = "postgres"
SUPABASE_USER     = "postgres.<project-ref>"
SUPABASE_PASSWORD = "SUA_SENHA_AQUI"
```

## Banco de origem (setup do Supabase)

Antes de extrair, o banco de origem precisa existir. Execute o script abaixo no
**Supabase → SQL Editor → New Query**. Ele cria as tabelas e popula o dataset da Loja Virtual
(o mesmo dos trabalhos 1 e 2).

```sql
-- ============================================================
-- Setup Supabase — LojaVirtualDB
-- ============================================================

-- 1. Remove tabelas se já existirem (ordem respeitando FKs)
DROP TABLE IF EXISTS pedidos  CASCADE;
DROP TABLE IF EXISTS produtos CASCADE;
DROP TABLE IF EXISTS clientes CASCADE;

-- 2. Cria tabelas
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

-- 3. Insere dados (mesmo dataset dos trabalhos 1 e 2)
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

-- 4. Validação
SELECT 'clientes' AS tabela, COUNT(*) AS total FROM clientes
UNION ALL SELECT 'produtos', COUNT(*) FROM produtos
UNION ALL SELECT 'pedidos',  COUNT(*) FROM pedidos;
```

## Resultado

Ao final, os dados brutos ficam disponíveis no Volume `/Volumes/workspace/landing/dados/` e como
tabelas no schema `landing`, prontos para serem ingeridos pela camada **Bronze**.
