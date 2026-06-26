# Databricks notebook source

# COMMAND ----------

# MAGIC %md
# MAGIC # 004 — Silver: Data Quality
# MAGIC ## Schema `bronze` → Schema `silver` (Delta Lake)
# MAGIC
# MAGIC Aplica regras de **Data Quality** nos dados do Bronze e grava no Silver.
# MAGIC
# MAGIC ### Regras de qualidade aplicadas
# MAGIC | Regra | Descrição |
# MAGIC |-------|-----------|
# MAGIC | Deduplicação | Remove registros com chave primária duplicada |
# MAGIC | Nulos | Filtra registros com campos obrigatórios nulos |
# MAGIC | Tipos | Garante tipos de dados corretos (data, decimal) |
# MAGIC | Strings | Trim e normalização de capitalização |
# MAGIC | Validação | Remove registros com valores inválidos (preço negativo, etc.) |
# MAGIC | Renomeação | Colunas em snake_case sem abreviações |
# MAGIC | Metadados | Adiciona `data_processamento` atualizada |

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Configuração

# COMMAND ----------

from pyspark.sql import functions as F

BRONZE_DB = "bronze"
SILVER_DB = "silver"

print(f"Bronze Schema : {BRONZE_DB}")
print(f"Silver Schema : {SILVER_DB}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Silver — Clientes

# COMMAND ----------

df_clientes_bronze = spark.table(f"{BRONZE_DB}.clientes")

print("Bronze — clientes (antes do DQ):")
df_clientes_bronze.show(truncate=False)

# COMMAND ----------

df_clientes_silver = (
    df_clientes_bronze
    # Deduplicação pela chave primária
    .dropDuplicates(["id"])
    # Remove registros com campos obrigatórios nulos
    .filter(F.col("id").isNotNull())
    .filter(F.col("nome").isNotNull())
    .filter(F.col("email").isNotNull())
    # Padronização: trim e capitalização
    .withColumn("nome",   F.initcap(F.trim(F.col("nome"))))
    .withColumn("email",  F.lower(F.trim(F.col("email"))))
    .withColumn("cidade", F.when(
        F.col("cidade").isNull(), F.lit("Nao Informado")
    ).otherwise(F.initcap(F.trim(F.col("cidade")))))
    # Renomear colunas (snake_case sem abreviações)
    .withColumnRenamed("id",     "id_cliente")
    .withColumnRenamed("nome",   "nome_cliente")
    .withColumnRenamed("email",  "email_cliente")
    .withColumnRenamed("cidade", "cidade_cliente")
    # Atualiza metadado e remove coluna de auditoria do bronze
    .withColumn("data_processamento", F.current_timestamp())
    .drop("nome_arquivo")
)

print(f"Registros Bronze : {df_clientes_bronze.count()}")
print(f"Registros Silver : {df_clientes_silver.count()}")

df_clientes_silver.write.format("delta").mode("overwrite").saveAsTable(f"{SILVER_DB}.clientes")
print(f"\nTabela `{SILVER_DB}.clientes` salva!")
df_clientes_silver.show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Silver — Produtos

# COMMAND ----------

df_produtos_bronze = spark.table(f"{BRONZE_DB}.produtos")

print("Bronze — produtos (antes do DQ):")
df_produtos_bronze.show(truncate=False)

# COMMAND ----------

df_produtos_silver = (
    df_produtos_bronze
    .dropDuplicates(["id"])
    .filter(F.col("id").isNotNull())
    .filter(F.col("nome").isNotNull())
    # Remove produtos com preço nulo ou negativo
    .filter(F.col("preco").isNotNull())
    .filter(F.col("preco") > 0)
    # Estoque negativo é normalizado para zero
    .withColumn("estoque",
        F.when(F.col("estoque").isNull() | (F.col("estoque") < 0), F.lit(0))
         .otherwise(F.col("estoque").cast("int"))
    )
    # Padronização
    .withColumn("nome",      F.initcap(F.trim(F.col("nome"))))
    .withColumn("categoria", F.initcap(F.trim(F.col("categoria"))))
    .withColumn("preco",     F.round(F.col("preco").cast("double"), 2))
    # Renomear colunas
    .withColumnRenamed("id",        "id_produto")
    .withColumnRenamed("nome",      "nome_produto")
    .withColumnRenamed("categoria", "categoria_produto")
    .withColumnRenamed("preco",     "preco_produto")
    .withColumnRenamed("estoque",   "estoque_produto")
    .withColumn("data_processamento", F.current_timestamp())
    .drop("nome_arquivo")
)

print(f"Registros Bronze : {df_produtos_bronze.count()}")
print(f"Registros Silver : {df_produtos_silver.count()}")

df_produtos_silver.write.format("delta").mode("overwrite").saveAsTable(f"{SILVER_DB}.produtos")
print(f"Tabela `{SILVER_DB}.produtos` salva!")
df_produtos_silver.show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Silver — Pedidos

# COMMAND ----------

df_pedidos_bronze = spark.table(f"{BRONZE_DB}.pedidos")

print("Bronze — pedidos (antes do DQ):")
df_pedidos_bronze.show(truncate=False)

# COMMAND ----------

STATUS_VALIDOS = ["entregue", "em_transito", "processando", "finalizado", "cancelado"]

df_pedidos_silver = (
    df_pedidos_bronze
    .dropDuplicates(["id"])
    .filter(F.col("id").isNotNull())
    .filter(F.col("cliente_id").isNotNull())
    .filter(F.col("produto_id").isNotNull())
    # Remove pedidos com valor nulo ou negativo
    .filter(F.col("valor_total").isNotNull())
    .filter(F.col("valor_total") > 0)
    # Remove pedidos com quantidade inválida
    .filter(F.col("quantidade").isNotNull())
    .filter(F.col("quantidade") > 0)
    # Normaliza status para lowercase sem espaços extras
    .withColumn("status", F.lower(F.trim(F.col("status"))))
    # Substitui status fora do domínio por 'desconhecido'
    .withColumn(
        "status",
        F.when(F.col("status").isin(STATUS_VALIDOS), F.col("status"))
         .otherwise(F.lit("desconhecido"))
    )
    # Garante tipo correto na data
    .withColumn("data_pedido",   F.to_date(F.col("data_pedido")))
    .withColumn("valor_total",   F.round(F.col("valor_total").cast("double"), 2))
    .withColumn("quantidade",    F.col("quantidade").cast("int"))
    # Renomear colunas
    .withColumnRenamed("id",          "id_pedido")
    .withColumnRenamed("cliente_id",  "id_cliente")
    .withColumnRenamed("produto_id",  "id_produto")
    .withColumnRenamed("quantidade",  "quantidade_pedido")
    .withColumnRenamed("valor_total", "valor_total_pedido")
    .withColumnRenamed("status",      "status_pedido")
    .withColumn("data_processamento", F.current_timestamp())
    .drop("nome_arquivo")
)

print(f"Registros Bronze : {df_pedidos_bronze.count()}")
print(f"Registros Silver : {df_pedidos_silver.count()}")

df_pedidos_silver.write.format("delta").mode("overwrite").saveAsTable(f"{SILVER_DB}.pedidos")
print(f"Tabela `{SILVER_DB}.pedidos` salva!")
df_pedidos_silver.show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Resumo de Data Quality

# COMMAND ----------

print("=== Tabelas no schema SILVER ===")
spark.sql(f"SHOW TABLES IN {SILVER_DB}").show(truncate=False)

print("\n=== Contagem de registros ===")
for tabela in ["clientes", "produtos", "pedidos"]:
    count = spark.sql(f"SELECT COUNT(*) FROM {SILVER_DB}.{tabela}").collect()[0][0]
    print(f"  silver.{tabela}: {count} registros")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Schema das tabelas Silver

# COMMAND ----------

for tabela in ["clientes", "produtos", "pedidos"]:
    print(f"\n--- Schema: silver.{tabela} ---")
    spark.sql(f"DESCRIBE {SILVER_DB}.{tabela}").show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ Silver (Data Quality) concluída!
# MAGIC
# MAGIC Dados limpos, validados e com colunas padronizadas gravados no schema Silver.
# MAGIC
# MAGIC Próximo passo → **005_Gold_Modelagem_Dimensional**
