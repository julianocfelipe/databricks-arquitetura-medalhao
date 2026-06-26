# Databricks notebook source

# COMMAND ----------

# MAGIC %md
# MAGIC # 002 — Landing: Extração do Banco de Dados
# MAGIC ## Fonte: Supabase (PostgreSQL) → Volume `/Volumes/<catalog>/landing/dados`
# MAGIC
# MAGIC Extrai todas as tabelas do banco **LojaVirtualDB** no Supabase
# MAGIC e grava como arquivos **CSV** na Landing Zone.
# MAGIC
# MAGIC ### Modelo de dados extraído
# MAGIC ```
# MAGIC clientes (id, nome, email, cidade)
# MAGIC produtos (id, nome, categoria, preco, estoque)
# MAGIC pedidos  (id, cliente_id, produto_id, quantidade, valor_total, data_pedido, status)
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Instalar o driver PostgreSQL (psycopg2)

# COMMAND ----------

# MAGIC %pip install psycopg2-binary

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Configuração da Conexão com Supabase

# COMMAND ----------
SUPABASE_HOST     = "aws-1-us-west-2.pooler.supabase.com"
SUPABASE_PORT     = "5432"
SUPABASE_DB       = "postgres"
SUPABASE_USER     = "postgres.cffpopikxclgtbuyyzgr"
SUPABASE_PASSWORD = "I8ntHq1cKA1mCJsF"

# Landing Zone como Volume do Unity Catalog (schema landing / volume dados)
CATALOG      = spark.sql("SELECT current_catalog()").collect()[0][0]
LANDING_PATH = f"/Volumes/{CATALOG}/landing/dados"
tabelas      = ["clientes", "produtos", "pedidos"]

print(f"Host    : {SUPABASE_HOST}")
print(f"Banco   : {SUPABASE_DB}")
print(f"Landing : {LANDING_PATH}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Extrair tabelas do Supabase e gravar na Landing Zone

# COMMAND ----------

import os
import psycopg2
import pandas as pd
from datetime import datetime

data_extracao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"Início da extração: {data_extracao}\n")

# Conecta no Supabase via psycopg2 (driver Python — funciona no serverless)
conn = psycopg2.connect(
    host=SUPABASE_HOST,
    port=SUPABASE_PORT,
    dbname=SUPABASE_DB,
    user=SUPABASE_USER,
    password=SUPABASE_PASSWORD,
    sslmode="require",
)

for tabela in tabelas:
    print(f"{'='*50}")
    print(f"Extraindo tabela: {tabela.upper()}")
    print(f"{'='*50}")

    # Lê a tabela inteira para um DataFrame pandas
    pdf = pd.read_sql(f"SELECT * FROM {tabela}", conn)
    print(f"Registros extraídos: {len(pdf)}")
    print(pdf.head().to_string(index=False))

    # Grava como CSV na Landing Zone (Volume do Unity Catalog) — formato original, sem Delta
    destino = f"{LANDING_PATH}/{tabela}"
    os.makedirs(destino, exist_ok=True)
    pdf.to_csv(f"{destino}/{tabela}.csv", index=False)

    print(f"Salvo em: {destino}/{tabela}.csv\n")

conn.close()
print(f"Extração finalizada em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Validação — Conteúdo da Landing Zone

# COMMAND ----------

print("=== Arquivos na Landing Zone ===\n")
for tabela in tabelas:
    arquivos = [f for f in dbutils.fs.ls(f"{LANDING_PATH}/{tabela}") if f.name.endswith(".csv")]
    for arq in arquivos:
        print(f"{tabela}: {arq.name}  ({arq.size} bytes)")

# COMMAND ----------

print("=== Prévia dos dados extraídos ===\n")
for tabela in tabelas:
    print(f"--- {tabela.upper()} ---")
    df_check = (
        spark.read
        .option("header", "true")
        .csv(f"{LANDING_PATH}/{tabela}")
    )
    df_check.show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ Extração concluída!
# MAGIC
# MAGIC Dados brutos gravados no Volume `/Volumes/<catalog>/landing/dados/`
# MAGIC
# MAGIC Próximo passo → **003_Bronze_Ingestao**
