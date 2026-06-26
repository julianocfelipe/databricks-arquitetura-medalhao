# Databricks notebook source

# COMMAND ----------

# MAGIC %md
# MAGIC # 002 — Landing: Extração do Banco de Dados
# MAGIC ## Fonte: Supabase (PostgreSQL) → DBFS `/FileStore/landing/dados`
# MAGIC
# MAGIC Extrai todas as tabelas do banco **LojaVirtualDB** no Supabase
# MAGIC e grava como arquivos **CSV** na Landing Zone.
# MAGIC
# MAGIC ### Pré-requisito obrigatório
# MAGIC Antes de rodar este notebook, instale a biblioteca Maven no cluster:
# MAGIC - Vá em **Compute → seu cluster → Libraries → Install New**
# MAGIC - Selecione **Maven** e cole a coordenada: `org.postgresql:postgresql:42.7.3`
# MAGIC - Aguarde a instalação e reinicie o cluster
# MAGIC
# MAGIC ### Modelo de dados extraído
# MAGIC ```
# MAGIC clientes (id, nome, email, cidade)
# MAGIC produtos (id, nome, categoria, preco, estoque)
# MAGIC pedidos  (id, cliente_id, produto_id, quantidade, valor_total, data_pedido, status)
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Configuração da Conexão com Supabase

# COMMAND ----------

# ⚠️ Substitua pelos dados do SEU projeto Supabase
# Acesse: supabase.com → seu projeto → Settings → Database → Connection string
SUPABASE_HOST     = "db.XXXXXXXXXX.supabase.co"   # ex: db.abcdefghij.supabase.co
SUPABASE_PORT     = "5432"
SUPABASE_DB       = "postgres"
SUPABASE_USER     = "postgres"
SUPABASE_PASSWORD = "SUA_SENHA_AQUI"               # senha definida ao criar o projeto

JDBC_URL = (
    f"jdbc:postgresql://{SUPABASE_HOST}:{SUPABASE_PORT}/{SUPABASE_DB}"
    f"?sslmode=require"
)

connection_properties = {
    "user":     SUPABASE_USER,
    "password": SUPABASE_PASSWORD,
    "driver":   "org.postgresql.Driver"
}

LANDING_PATH = "/FileStore/landing/dados"
tabelas      = ["clientes", "produtos", "pedidos"]

print(f"Host   : {SUPABASE_HOST}")
print(f"Banco  : {SUPABASE_DB}")
print(f"Driver : org.postgresql.Driver")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Extrair tabelas do Supabase e gravar na Landing Zone

# COMMAND ----------

from datetime import datetime

data_extracao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"Início da extração: {data_extracao}\n")

for tabela in tabelas:
    print(f"{'='*50}")
    print(f"Extraindo tabela: {tabela.upper()}")
    print(f"{'='*50}")

    df = spark.read.jdbc(
        url=JDBC_URL,
        table=tabela,
        properties=connection_properties
    )

    total = df.count()
    print(f"Registros extraídos: {total}")
    df.show(truncate=False)

    # Salva como CSV no DBFS (landing zone) — formato original, sem Delta
    (
        df.coalesce(1)
        .write
        .mode("overwrite")
        .option("header", "true")
        .csv(f"{LANDING_PATH}/{tabela}")
    )

    print(f"Salvo em: dbfs:{LANDING_PATH}/{tabela}/\n")

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
# MAGIC Dados brutos gravados em `dbfs:/FileStore/landing/dados/`
# MAGIC
# MAGIC Próximo passo → **003_Bronze_Ingestao**
