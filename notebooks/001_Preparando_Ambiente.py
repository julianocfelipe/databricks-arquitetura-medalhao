# Databricks notebook source

# COMMAND ----------

# MAGIC %md
# MAGIC # 001 — Preparando Ambiente
# MAGIC ## Arquitetura Medalhão · Loja Virtual
# MAGIC
# MAGIC Este notebook cria todos os **schemas** e diretórios necessários para a arquitetura medalhão.
# MAGIC
# MAGIC | Schema   | Descrição |
# MAGIC |----------|-----------|
# MAGIC | `landing` | Zona de entrada — arquivos CSV brutos |
# MAGIC | `bronze`  | Ingestão em Delta Lake (histórico completo) |
# MAGIC | `silver`  | Dados tratados com Data Quality aplicada |
# MAGIC | `gold`    | Modelo dimensional Ralph Kimball (consumo) |

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Remover ambiente anterior (execução limpa)

# COMMAND ----------

spark.sql("DROP SCHEMA IF EXISTS landing CASCADE")
spark.sql("DROP SCHEMA IF EXISTS bronze CASCADE")
spark.sql("DROP SCHEMA IF EXISTS silver CASCADE")
spark.sql("DROP SCHEMA IF EXISTS gold CASCADE")

dbutils.fs.rm("/FileStore/landing/dados", recurse=True)

print("Ambiente anterior removido com sucesso.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Criar schemas da Arquitetura Medalhão

# COMMAND ----------

spark.sql("""
    CREATE SCHEMA IF NOT EXISTS landing
    COMMENT 'Zona de ingestão — arquivos brutos CSV extraídos do banco de origem'
""")

spark.sql("""
    CREATE SCHEMA IF NOT EXISTS bronze
    COMMENT 'Dados brutos em Delta Lake — histórico completo imutável'
""")

spark.sql("""
    CREATE SCHEMA IF NOT EXISTS silver
    COMMENT 'Dados tratados com regras de Data Quality aplicadas'
""")

spark.sql("""
    CREATE SCHEMA IF NOT EXISTS gold
    COMMENT 'Modelo dimensional Ralph Kimball — consumo analítico e BI'
""")

print("Schemas criados com sucesso!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Validar schemas criados

# COMMAND ----------

print("=== Schemas disponíveis ===")
spark.sql("SHOW DATABASES").show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Criar diretórios da Landing Zone no DBFS

# COMMAND ----------

tabelas = ["clientes", "produtos", "pedidos"]

for tabela in tabelas:
    dbutils.fs.mkdirs(f"/FileStore/landing/dados/{tabela}")

print("Diretórios de Landing Zone criados:")
display(dbutils.fs.ls("/FileStore/landing/dados/"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ Ambiente pronto!
# MAGIC
# MAGIC **Schemas criados:** `landing` · `bronze` · `silver` · `gold`
# MAGIC
# MAGIC Próximo passo → **002_Landing_Extracao**
