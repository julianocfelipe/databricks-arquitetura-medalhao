# Camada Landing

> Notebook: `002_Landing_Extracao.py`

A **Landing** é a camada provisória responsável pela **primeira ingestão** dos dados no Data Lake.
Os dados são gravados no **formato original da origem** — neste trabalho, **CSV** (origem relacional).

## O que a camada faz

- Conecta no banco de origem (**Supabase / PostgreSQL**) via **psycopg2**
- Extrai **todas as tabelas** (`clientes`, `produtos`, `pedidos`)
- Grava cada tabela como **CSV** no Volume `/Volumes/<catalog>/landing/dados/{tabela}/`

```python
%pip install psycopg2-binary
dbutils.library.restartPython()

import psycopg2, pandas as pd, os

conn = psycopg2.connect(host=SUPABASE_HOST, port=SUPABASE_PORT, dbname=SUPABASE_DB,
                        user=SUPABASE_USER, password=SUPABASE_PASSWORD, sslmode="require")

pdf = pd.read_sql(f"SELECT * FROM {tabela}", conn)
os.makedirs(f"{LANDING_PATH}/{tabela}", exist_ok=True)
pdf.to_csv(f"{LANDING_PATH}/{tabela}/{tabela}.csv", index=False)
```

!!! info "Databricks Free Edition é serverless"
    O Free Edition **não tem cluster clássico** nem aba *Libraries* — não dá para instalar driver
    **Maven**. Por isso a extração usa **psycopg2** (driver Python), instalado no próprio notebook
    com `%pip install psycopg2-binary`. A Landing Zone também não usa DBFS (`/FileStore`, restrito
    no serverless), e sim um **Volume** do Unity Catalog: `/Volumes/<catalog>/landing/dados`.

!!! warning "Conexão IPv6 vs IPv4 (Supabase)"
    A conexão **direta** (`db.xxxx.supabase.co`) costuma ser apenas IPv6 e pode dar timeout a partir
    do Databricks serverless. Se isso acontecer, use os dados do **Session Pooler** (IPv4) do Supabase:
    host `aws-0-<regiao>.pooler.supabase.com` e usuário `postgres.<project-ref>`.

## Configuração da conexão

No início do notebook `002_Landing_Extracao.py`, preencha as credenciais do **seu** projeto Supabase
(`Settings → Database → Connection string`):

```python
SUPABASE_HOST     = "db.XXXXXXXXXX.supabase.co"
SUPABASE_PORT     = "5432"
SUPABASE_DB       = "postgres"
SUPABASE_USER     = "postgres"
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

Ao final, os dados brutos ficam disponíveis no Volume `/Volumes/<catalog>/landing/dados/`, prontos
para serem ingeridos pela camada **Bronze**.
