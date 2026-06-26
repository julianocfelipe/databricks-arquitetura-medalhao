# Camada Bronze

> Notebook: `003_Bronze_Ingestao.py`

A **Bronze** é a cópia da camada Landing, agora em **Delta Lake**. Mantém o **histórico completo dos
dados brutos** (ainda não processados), com suporte a ACID e *time travel*.

## O que a camada faz

- Lê os arquivos **CSV** da Landing Zone (`/Volumes/<catalog>/landing/dados/{tabela}`)
- Adiciona **metadados de auditoria**
- Grava como **tabela Delta gerenciada** no schema `bronze`

```python
df_bronze = (
    df_landing
    .withColumn("nome_arquivo",       F.input_file_name())
    .withColumn("data_processamento", F.current_timestamp())
)

(df_bronze.write
   .format("delta")
   .mode("overwrite")
   .saveAsTable(f"bronze.{tabela}"))
```

## Características

- **Formato Delta** (ACID, metadados, time travel)
- **Dados imutáveis** (apenas leitura) — cópia fiel da landing, sem transformação de valores
- **Metadados adicionados**: `nome_arquivo` (origem) e `data_processamento` (carimbo de tempo)
- Mantém o histórico completo dos dados brutos

## Validações do notebook

O notebook também demonstra recursos do Delta Lake:

- `DESCRIBE DETAIL bronze.{tabela}` — formato, nº de arquivos, tamanho
- `DESCRIBE HISTORY bronze.{tabela}` — histórico de versões (**time travel**)
- `SHOW TABLES IN bronze` + contagem de registros por tabela

## Resultado

Tabelas Delta `bronze.clientes`, `bronze.produtos` e `bronze.pedidos`, prontas para receber as
regras de **Data Quality** na camada Silver.
