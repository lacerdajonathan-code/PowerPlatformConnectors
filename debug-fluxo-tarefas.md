# 🔍 DEBUG - POR QUE AS TAREFAS NÃO ESTÃO SENDO CRIADAS

## 🚨 POSSÍVEIS CAUSAS DO PROBLEMA

### 1️⃣ **PROBLEMA: Nome do Bucket não coincide**
- O nome no Excel está EXATAMENTE igual ao Planner?
- Tem espaços extras? Maiúsculas/minúsculas diferentes?

### 2️⃣ **PROBLEMA: Verificação de tarefa sempre encontra algo**
- A comparação do título pode estar errada
- Pode estar comparando campos diferentes

### 3️⃣ **PROBLEMA: A condição está invertida**
- Verificar se a lógica está correta

---

## 🐛 ADICIONE AÇÕES DE DEBUG

### PASSO 1: Debug após "Encontrar_Bucket_Correspondente"

1. Logo APÓS "Encontrar_Bucket_Correspondente"
2. Clique em **"Nova etapa"**
3. Pesquise e adicione **"Compor"**
4. Renomeie para: `Debug_Bucket_Encontrado`
5. No campo **Entradas**, adicione:

```json
{
  "Bucket_Procurado": "@{items('Processar_Cada_Linha_Excel')?['Bucket']}",
  "Buckets_Encontrados": "@{length(body('Encontrar_Bucket_Correspondente'))}",
  "Resultado": "@{body('Encontrar_Bucket_Correspondente')}"
}
```

### PASSO 2: Debug após "Verificar_Tarefa_Existe"

1. Logo APÓS "Verificar_Tarefa_Existe"
2. Adicione outra ação **"Compor"**
3. Renomeie para: `Debug_Tarefa_Verificacao`
4. No campo **Entradas**:

```json
{
  "Tarefa_Procurada": "@{items('Processar_Cada_Linha_Excel')?['Nome da Tarefa']}",
  "Tarefas_Encontradas": "@{length(body('Verificar_Tarefa_Existe'))}",
  "Resultado": "@{body('Verificar_Tarefa_Existe')}"
}
```

### PASSO 3: Debug na Condição

1. No bloco **"Não"** da condição
2. Modifique o "Log_Tarefa_Ja_Existe" para:

```json
{
  "Motivo": "Tarefa não criada",
  "Nome_Tarefa": "@{items('Processar_Cada_Linha_Excel')?['Nome da Tarefa']}",
  "Bucket_Nome": "@{items('Processar_Cada_Linha_Excel')?['Bucket']}",
  "Bucket_Encontrado": "@{length(body('Encontrar_Bucket_Correspondente'))}",
  "Tarefa_Ja_Existe": "@{length(body('Verificar_Tarefa_Existe'))}"
}
```

---

## ⚠️ VERIFICAÇÕES CRÍTICAS

### VERIFICAÇÃO 1: A Condição está correta?

A condição DEVE ser:
```
SE:
  length(body('Verificar_Tarefa_Existe')) é igual a 0
  E
  length(body('Encontrar_Bucket_Correspondente')) é MAIOR QUE 0
```

⚠️ **CONFIRME:**
- O segundo é "MAIOR QUE" e não "igual a"?
- Está usando AND e não OR?

### VERIFICAÇÃO 2: Os nomes dos campos estão corretos?

No Excel, os nomes das colunas são EXATAMENTE:
- `Nome da Tarefa` (não "Nome_da_Tarefa" ou "NomeTarefa")
- `Bucket` (não "Buckets" ou "bucket")
- `Data de início` (com acento?)
- `Data de conclusão` (com til?)

### VERIFICAÇÃO 3: Comparação de Títulos

Em "Verificar_Tarefa_Existe", o campo "Onde" deve ser:
- Esquerda: `item()?['title']` (campo do Planner)
- Direita: `items('Processar_Cada_Linha_Excel')?['Nome da Tarefa']` (campo do Excel)

---

## 🔧 SOLUÇÃO ALTERNATIVA - LÓGICA SIMPLIFICADA

Se continuar não funcionando, vamos simplificar:

### OPÇÃO A: Remover verificação de duplicatas temporariamente

1. **DELETE** a ação "Verificar_Tarefa_Existe"
2. **MODIFIQUE** a condição para apenas:

```
SE:
  length(body('Encontrar_Bucket_Correspondente')) é maior que 0
```

Isso vai criar tarefas duplicadas, mas pelo menos confirmamos se o problema é na verificação.

### OPÇÃO B: Criar sem condição (teste)

1. **MOVA** "Criar_Nova_Tarefa_Planner" para FORA da condição
2. Coloque direto após "Encontrar_Bucket_Correspondente"
3. Teste se cria as tarefas

Se funcionar, o problema está na condição!

---

## 📊 ANÁLISE DO HISTÓRICO DE EXECUÇÃO

### Como verificar o que está acontecendo:

1. Vá em **"Histórico de execuções"**
2. Clique na última execução
3. Expanda cada ação e veja:

#### Em "Encontrar_Bucket_Correspondente":
- **Entradas:** Qual bucket está procurando?
- **Saídas:** Encontrou algo? (deve ter um array com 1 item)

#### Em "Verificar_Tarefa_Existe":
- **Entradas:** Qual tarefa está procurando?
- **Saídas:** Encontrou algo? (deve ter array vazio [])

#### Na "Condição":
- **Resultado:** Foi para "Sim" ou "Não"?

---

## 🎯 TESTE DIAGNÓSTICO RÁPIDO

### Crie uma planilha de teste SIMPLES:

| Nome da Tarefa | Bucket |
|----------------|--------|
| TESTE123       | To Do  |

### Verifique:
1. O bucket "To Do" existe EXATAMENTE assim no Planner?
2. A tarefa "TESTE123" NÃO existe no Planner?

### Execute e veja:
- Se criar: O problema era nos dados
- Se não criar: Veja os debugs para entender

---

## 💡 PROBLEMAS MAIS COMUNS ENCONTRADOS

### 1. **Espaços invisíveis**
```
Excel:   "To Do " (com espaço no final)
Planner: "To Do" (sem espaço)
Resultado: Não encontra o bucket!
```

### 2. **Maiúsculas/Minúsculas**
```
Excel:   "to do"
Planner: "To Do"
Resultado: Depende da configuração, pode não encontrar
```

### 3. **Caracteres especiais**
```
Excel:   "Bucket – Teste" (travessão)
Planner: "Bucket - Teste" (hífen)
Resultado: Não encontra!
```

### 4. **Campos vazios no Excel**
Se o campo "Bucket" estiver vazio em alguma linha, pode dar erro.

---

## 🔴 CORREÇÃO DEFINITIVA

### Se nada funcionar, vamos refazer a lógica:

```json
{
  "Processar_Cada_Linha_Excel": {
    "type": "Foreach",
    "foreach": "@body('Obter_Dados_Excel')?['value']",
    "actions": {
      "Validar_Campos_Obrigatorios": {
        "type": "If",
        "expression": {
          "and": [
            {
              "not": {
                "equals": [
                  "@items('Processar_Cada_Linha_Excel')?['Nome da Tarefa']",
                  ""
                ]
              }
            },
            {
              "not": {
                "equals": [
                  "@items('Processar_Cada_Linha_Excel')?['Bucket']",
                  ""
                ]
              }
            }
          ]
        },
        "actions": {
          "Encontrar_Bucket_Correspondente": {
            "type": "Query",
            "inputs": {
              "from": "@body('Listar_Todos_Buckets')?['value']",
              "where": "@equals(toLower(trim(item()?['name'])), toLower(trim(items('Processar_Cada_Linha_Excel')?['Bucket'])))"
            }
          },
          "Verificar_Se_Bucket_Existe": {
            "type": "If",
            "expression": {
              "greater": [
                "@length(body('Encontrar_Bucket_Correspondente'))",
                0
              ]
            },
            "actions": {
              "Criar_Nova_Tarefa_Planner": {
                "type": "OpenApiConnection",
                "inputs": {
                  "parameters": {
                    "body/groupId": "332dd89f-c104-4ae6-96a9-6a45b8ec6f6f",
                    "body/planId": "XLO7WAvmFEGU07P6t_UH4WQAF9gY",
                    "body/title": "@items('Processar_Cada_Linha_Excel')?['Nome da Tarefa']",
                    "body/bucketId": "@first(body('Encontrar_Bucket_Correspondente'))?['id']"
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

Esta versão:
1. Valida campos obrigatórios primeiro
2. Usa `toLower()` e `trim()` para ignorar maiúsculas e espaços
3. Simplifica a lógica (remove verificação de duplicatas por enquanto)