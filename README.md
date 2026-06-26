# Trabalho 3 — Databricks: Arquitetura Medalhão

Pipeline de dados no **Databricks Free Edition** implementando a **Arquitetura Medalhão** (Landing → Bronze → Silver → Gold) com Jobs & Pipelines.

## Contexto

Este trabalho é um complemento dos trabalhos 1 e 2, migrando o mesmo dataset (Loja Virtual) para uma solução **PaaS na nuvem** com Databricks.

| Trabalho | Tecnologias | Foco |
|----------|-------------|------|
| 1 | Apache Spark + Delta Lake (local) | Delta Lake e DML |
| 2 | SQL Server + MinIO + Spark (Docker) | Ingestão Landing → Bronze |
| **3** | **Databricks + Supabase** | **Pipeline completo Medalhão** |

## Arquitetura

```
Supabase (PostgreSQL)
       │
       ▼
  LANDING/DADOS          ← CSV bruto extraído via JDBC
       │
       ▼
    BRONZE                ← Delta Lake + metadados de auditoria
       │
       ▼
    SILVER                ← Delta Lake + Data Quality
       │
       ▼
     GOLD                 ← Delta Lake + Star Schema (Ralph Kimball)
```

## Modelo de dados

### Origem (Supabase)
- `clientes` (id, nome, email, cidade)
- `produtos` (id, nome, categoria, preco, estoque)
- `pedidos` (id, cliente_id, produto_id, quantidade, valor_total, data_pedido, status)

### Gold — Star Schema
```
         dim_clientes
              │
dim_tempo ─── fato_pedidos ─── dim_produtos
```

| Tabela | Tipo | Chave |
|--------|------|-------|
| `dim_clientes` | Dimensão | sk_cliente |
| `dim_produtos` | Dimensão | sk_produto |
| `dim_tempo` | Dimensão | sk_tempo (YYYYMMDD) |
| `fato_pedidos` | Fato | sk_pedido |

## Notebooks

| Notebook | Etapa | Descrição |
|----------|-------|-----------|
| `001_Preparando_Ambiente.py` | Setup | Cria schemas e diretórios |
| `002_Landing_Extracao.py` | Landing | Extrai do Supabase → CSV no DBFS |
| `003_Bronze_Ingestao.py` | Bronze | CSV → Delta Lake com metadados |
| `004_Silver_Data_Quality.py` | Silver | Data Quality + padronização |
| `005_Gold_Modelagem_Dimensional.py` | Gold | Star Schema (Ralph Kimball) |

## Tecnologias

- [Databricks Free Edition](https://www.databricks.com/learn/freeedition)
- [Supabase](https://supabase.com) — PostgreSQL cloud (banco de origem)
- Delta Lake — formato de armazenamento
- Apache Spark (PySpark) — processamento
- Jobs & Pipelines — orquestração

## Como executar

### Pré-requisitos
1. Conta no [Databricks Community Edition](https://community.cloud.databricks.com)
2. Conta no [Supabase](https://supabase.com)
3. Cluster criado com a biblioteca Maven: `org.postgresql:postgresql:42.7.3`

### Passo a passo
1. Execute o script `sql/setup_supabase.sql` no SQL Editor do Supabase
2. Importe os notebooks da pasta `notebooks/` no workspace do Databricks
3. Configure as credenciais do Supabase no notebook `002_Landing_Extracao.py`
4. Execute os notebooks na ordem (001 → 002 → 003 → 004 → 005)
5. Ou execute o **Job** criado para automação completa

## Estrutura do repositório

```
├── notebooks/               # Notebooks Databricks
│   ├── 001_Preparando_Ambiente.py
│   ├── 002_Landing_Extracao.py
│   ├── 003_Bronze_Ingestao.py
│   ├── 004_Silver_Data_Quality.py
│   └── 005_Gold_Modelagem_Dimensional.py
├── sql/
│   └── setup_supabase.sql   # Script de criação do banco de origem
├── docs/                    # Documentação e assets
└── README.md
```

## Documentação

Consulte a [documentação completa](https://seu-usuario.github.io/trabalho3-databricks-medalhao) para detalhes da arquitetura e screenshots.
