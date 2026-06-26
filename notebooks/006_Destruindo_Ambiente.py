# Databricks notebook source

# COMMAND ----------

# MAGIC %md
# MAGIC # 006 — Destruindo o Ambiente
# MAGIC ## Arquitetura Medalhão · Loja Virtual
# MAGIC
# MAGIC Remove **todos** os schemas da arquitetura medalhão para começar do zero.
# MAGIC
# MAGIC | Schema | O que é apagado |
# MAGIC |--------|-----------------|
# MAGIC | `bronze` | Tabelas Delta da camada Bronze |
# MAGIC | `silver` | Tabelas Delta da camada Silver |
# MAGIC | `gold`   | Tabelas dimensionais da camada Gold |
# MAGIC | `landing` | Volume `dados` (CSV brutos) + schema |
# MAGIC
# MAGIC > ⚠️ **Atenção:** `DROP SCHEMA ... CASCADE` apaga todas as tabelas, volumes e dados
# MAGIC > de cada schema. Use apenas quando quiser reiniciar o ambiente.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Remover todos os schemas (CASCADE)

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Apagar todas as tabelas da camada bronze
# MAGIC DROP SCHEMA IF EXISTS workspace.bronze CASCADE;
# MAGIC
# MAGIC -- Apagar todas as tabelas da camada silver
# MAGIC DROP SCHEMA IF EXISTS workspace.silver CASCADE;
# MAGIC
# MAGIC -- Apagar todas as tabelas da camada gold
# MAGIC DROP SCHEMA IF EXISTS workspace.gold CASCADE;
# MAGIC
# MAGIC -- Apagar todas as tabelas e volumes da camada landing
# MAGIC DROP SCHEMA IF EXISTS workspace.landing CASCADE;

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Confirmar se tudo foi limpo

# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW SCHEMAS IN workspace;

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ Ambiente destruído!
# MAGIC
# MAGIC Os schemas `landing` · `bronze` · `silver` · `gold` foram removidos.
# MAGIC
# MAGIC Para reconstruir o pipeline → execute novamente a partir de **001_Preparando_Ambiente**.
