# Databricks notebook source

# COMMAND ----------

# MAGIC %md
# MAGIC # 003 — Bronze: Ingestão Delta Lake
# MAGIC ## Landing Zone → Schema `bronze` (Delta Lake)
# MAGIC
# MAGIC Lê os arquivos CSV da Landing Zone e grava no formato **Delta Lake**
# MAGIC no schema Bronze, adicionando colunas de metadados.
# MAGIC
# MAGIC ### Características da camada Bronze
# MAGIC - Cópia fiel dos dados da landing (sem transformações nos valores)
# MAGIC - Histórico completo dos dados brutos
# MAGIC - Formato **Delta Lake** com suporte a ACID e time travel
# MAGIC - Metadados adicionados: `nome_arquivo`, `data_processamento`
# MAGIC - Particionado por data de processamento

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Configuração

# COMMAND ----------

from pyspark.sql import functions as F

# Landing Zone como Volume do Unity Catalog (mesmo caminho usado no notebook 002)
CATALOG      = spark.sql("SELECT current_catalog()").collect()[0][0]
LANDING_PATH = f"/Volumes/{CATALOG}/landing/dados"
BRONZE_DB    = "bronze"
tabelas      = ["clientes", "produtos", "pedidos"]

print(f"Landing Path: {LANDING_PATH}")
print(f"Bronze Schema: {BRONZE_DB}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Ingestão: CSV (Landing) → Delta Lake (Bronze)

# COMMAND ----------

for tabela in tabelas:
    print(f"\n{'='*55}")
    print(f"  Processando: {tabela.upper()}")
    print(f"{'='*55}")

    # Lê o CSV da landing zone com schema inferido
    df_landing = (
        spark.read
        .option("header", "true")
        .option("inferSchema", "true")
        .csv(f"{LANDING_PATH}/{tabela}")
    )

    print(f"Registros lidos da landing: {df_landing.count()}")
    print("\nSchema original:")
    df_landing.printSchema()

    # Adiciona colunas de metadados (auditoria)
    # Obs.: input_file_name() não é suportado no Unity Catalog → usa a coluna _metadata.file_path
    df_bronze = (
        df_landing
        .withColumn("nome_arquivo",       F.col("_metadata.file_path"))
        .withColumn("data_processamento", F.current_timestamp())
    )

    # Salva como Delta no schema bronze (managed table)
    (
        df_bronze
        .write
        .format("delta")
        .mode("overwrite")
        .saveAsTable(f"{BRONZE_DB}.{tabela}")
    )

    print(f"\nTabela `{BRONZE_DB}.{tabela}` criada com sucesso!")
    spark.sql(f"SELECT * FROM {BRONZE_DB}.{tabela}").show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Validação — Detalhes das tabelas Delta

# COMMAND ----------

for tabela in tabelas:
    print(f"\n--- Detalhes: bronze.{tabela} ---")
    spark.sql(f"""
        DESCRIBE DETAIL {BRONZE_DB}.{tabela}
    """).select("format", "numFiles", "sizeInBytes", "createdAt").show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Histórico Delta Lake (Time Travel)

# COMMAND ----------

for tabela in tabelas:
    print(f"\n--- Histórico: bronze.{tabela} ---")
    spark.sql(f"""
        DESCRIBE HISTORY {BRONZE_DB}.{tabela}
    """).select("version", "timestamp", "operation", "operationMetrics").show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Resumo da camada Bronze

# COMMAND ----------

print("=== Tabelas no schema BRONZE ===")
spark.sql(f"SHOW TABLES IN {BRONZE_DB}").show(truncate=False)

print("\n=== Contagem de registros ===")
for tabela in tabelas:
    count = spark.sql(f"SELECT COUNT(*) FROM {BRONZE_DB}.{tabela}").collect()[0][0]
    print(f"  bronze.{tabela}: {count} registros")

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ Bronze concluída!
# MAGIC
# MAGIC Dados brutos ingeridos em formato Delta Lake com metadados de auditoria.
# MAGIC
# MAGIC Próximo passo → **004_Silver_Data_Quality**
