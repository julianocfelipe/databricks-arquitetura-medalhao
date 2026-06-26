# Databricks notebook source

# COMMAND ----------

# MAGIC %md
# MAGIC # 005 — Gold: Modelagem Dimensional
# MAGIC ## Schema `silver` → Schema `gold` (Ralph Kimball — Star Schema)
# MAGIC
# MAGIC Constrói o **Star Schema** a partir dos dados tratados no Silver.
# MAGIC
# MAGIC ```
# MAGIC              dim_clientes
# MAGIC                   │
# MAGIC   dim_tempo ──── fato_pedidos ──── dim_produtos
# MAGIC ```
# MAGIC
# MAGIC | Tabela          | Tipo      | Descrição                          |
# MAGIC |-----------------|-----------|------------------------------------|
# MAGIC | `dim_clientes`  | Dimensão  | Cadastro de clientes               |
# MAGIC | `dim_produtos`  | Dimensão  | Catálogo de produtos               |
# MAGIC | `dim_tempo`     | Dimensão  | Calendário analítico (datas)       |
# MAGIC | `fato_pedidos`  | Fato      | Transações de vendas               |

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Configuração

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.window import Window

SILVER_DB = "silver"
GOLD_DB   = "gold"

print(f"Silver Schema : {SILVER_DB}")
print(f"Gold Schema   : {GOLD_DB}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. dim_clientes
# MAGIC
# MAGIC Dimensão de clientes com surrogate key gerada.

# COMMAND ----------

df_clientes = spark.table(f"{SILVER_DB}.clientes")

# Gera surrogate key ordenada pelo id natural
w_cli = Window.orderBy("id_cliente")

dim_clientes = (
    df_clientes
    .withColumn("sk_cliente", F.row_number().over(w_cli))
    .select(
        "sk_cliente",
        "id_cliente",
        "nome_cliente",
        "email_cliente",
        "cidade_cliente"
    )
)

dim_clientes.write.format("delta").mode("overwrite").saveAsTable(f"{GOLD_DB}.dim_clientes")
print("dim_clientes criada:")
spark.table(f"{GOLD_DB}.dim_clientes").show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. dim_produtos
# MAGIC
# MAGIC Dimensão de produtos com surrogate key gerada.

# COMMAND ----------

df_produtos = spark.table(f"{SILVER_DB}.produtos")

w_prod = Window.orderBy("id_produto")

dim_produtos = (
    df_produtos
    .withColumn("sk_produto", F.row_number().over(w_prod))
    .select(
        "sk_produto",
        "id_produto",
        "nome_produto",
        "categoria_produto",
        "preco_produto"
    )
)

dim_produtos.write.format("delta").mode("overwrite").saveAsTable(f"{GOLD_DB}.dim_produtos")
print("dim_produtos criada:")
spark.table(f"{GOLD_DB}.dim_produtos").show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. dim_tempo
# MAGIC
# MAGIC Dimensão de tempo gerada a partir das datas únicas dos pedidos.
# MAGIC A surrogate key `sk_tempo` é o inteiro `YYYYMMDD` para facilitar joins e ordenação.

# COMMAND ----------

df_pedidos = spark.table(f"{SILVER_DB}.pedidos")

dim_tempo = (
    df_pedidos
    .select(F.col("data_pedido"))
    .distinct()
    .filter(F.col("data_pedido").isNotNull())
    .withColumn("sk_tempo",      F.date_format(F.col("data_pedido"), "yyyyMMdd").cast("int"))
    .withColumn("data_completa", F.col("data_pedido"))
    .withColumn("ano",           F.year(F.col("data_pedido")))
    .withColumn("mes",           F.month(F.col("data_pedido")))
    .withColumn("dia",           F.dayofmonth(F.col("data_pedido")))
    .withColumn("trimestre",     F.quarter(F.col("data_pedido")))
    .withColumn("nome_mes",      F.date_format(F.col("data_pedido"), "MMMM"))
    .withColumn("dia_semana",    F.date_format(F.col("data_pedido"), "EEEE"))
    .select(
        "sk_tempo", "data_completa", "ano", "mes",
        "dia", "trimestre", "nome_mes", "dia_semana"
    )
    .orderBy("sk_tempo")
)

dim_tempo.write.format("delta").mode("overwrite").saveAsTable(f"{GOLD_DB}.dim_tempo")
print("dim_tempo criada:")
spark.table(f"{GOLD_DB}.dim_tempo").show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. fato_pedidos
# MAGIC
# MAGIC Tabela fato com chaves estrangeiras (surrogate keys) para todas as dimensões.

# COMMAND ----------

df_silver_pedidos = spark.table(f"{SILVER_DB}.pedidos")
df_dim_clientes   = spark.table(f"{GOLD_DB}.dim_clientes")
df_dim_produtos   = spark.table(f"{GOLD_DB}.dim_produtos")
df_dim_tempo      = spark.table(f"{GOLD_DB}.dim_tempo")

# Gera surrogate key para a fato
w_fat = Window.orderBy("id_pedido")

fato_pedidos = (
    df_silver_pedidos
    # Resolve sk_cliente via join com dim_clientes
    .join(
        df_dim_clientes.select("sk_cliente", "id_cliente"),
        on="id_cliente",
        how="left"
    )
    # Resolve sk_produto via join com dim_produtos
    .join(
        df_dim_produtos.select("sk_produto", "id_produto"),
        on="id_produto",
        how="left"
    )
    # Resolve sk_tempo via join com dim_tempo
    .join(
        df_dim_tempo.select("sk_tempo", "data_completa"),
        df_silver_pedidos["data_pedido"] == df_dim_tempo["data_completa"],
        how="left"
    )
    .withColumn("sk_pedido", F.row_number().over(w_fat))
    .select(
        "sk_pedido",
        "id_pedido",
        "sk_cliente",
        "sk_produto",
        "sk_tempo",
        "quantidade_pedido",
        "valor_total_pedido",
        "status_pedido",
        F.current_timestamp().alias("data_processamento")
    )
)

fato_pedidos.write.format("delta").mode("overwrite").saveAsTable(f"{GOLD_DB}.fato_pedidos")
print("fato_pedidos criada:")
spark.table(f"{GOLD_DB}.fato_pedidos").show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Análises de validação — Star Schema em ação

# COMMAND ----------

# Receita total por categoria de produto
print("=== Receita por categoria de produto ===")
spark.sql(f"""
    SELECT
        p.categoria_produto,
        COUNT(f.id_pedido)         AS total_pedidos,
        SUM(f.quantidade_pedido)   AS unidades_vendidas,
        SUM(f.valor_total_pedido)  AS receita_total
    FROM {GOLD_DB}.fato_pedidos f
    JOIN {GOLD_DB}.dim_produtos  p ON f.sk_produto = p.sk_produto
    GROUP BY p.categoria_produto
    ORDER BY receita_total DESC
""").show(truncate=False)

# COMMAND ----------

# Receita por cidade do cliente
print("=== Receita por cidade ===")
spark.sql(f"""
    SELECT
        c.cidade_cliente,
        COUNT(f.id_pedido)        AS total_pedidos,
        SUM(f.valor_total_pedido) AS receita_total
    FROM {GOLD_DB}.fato_pedidos f
    JOIN {GOLD_DB}.dim_clientes c ON f.sk_cliente = c.sk_cliente
    GROUP BY c.cidade_cliente
    ORDER BY receita_total DESC
""").show(truncate=False)

# COMMAND ----------

# Pedidos por período (ano/mês)
print("=== Pedidos por mês ===")
spark.sql(f"""
    SELECT
        t.ano,
        t.mes,
        t.nome_mes,
        COUNT(f.id_pedido)        AS total_pedidos,
        SUM(f.valor_total_pedido) AS receita_total
    FROM {GOLD_DB}.fato_pedidos f
    JOIN {GOLD_DB}.dim_tempo t ON f.sk_tempo = t.sk_tempo
    GROUP BY t.ano, t.mes, t.nome_mes
    ORDER BY t.ano, t.mes
""").show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Resumo do schema Gold

# COMMAND ----------

print("=== Tabelas no schema GOLD ===")
spark.sql(f"SHOW TABLES IN {GOLD_DB}").show(truncate=False)

print("\n=== Contagem de registros ===")
for tabela in ["dim_clientes", "dim_produtos", "dim_tempo", "fato_pedidos"]:
    count = spark.sql(f"SELECT COUNT(*) FROM {GOLD_DB}.{tabela}").collect()[0][0]
    print(f"  gold.{tabela}: {count} registros")

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ Gold (Modelagem Dimensional) concluída!
# MAGIC
# MAGIC ### Star Schema criado:
# MAGIC - `gold.dim_clientes` — dimensão de clientes
# MAGIC - `gold.dim_produtos` — dimensão de produtos
# MAGIC - `gold.dim_tempo`    — dimensão de tempo (calendário)
# MAGIC - `gold.fato_pedidos` — fato de vendas (métricas)
# MAGIC
# MAGIC **Pipeline Medallion Architecture completo!**
# MAGIC `Landing → Bronze → Silver → Gold`
