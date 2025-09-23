# 🔄 LÓGICA REORGANIZADA - VERIFICAR TAREFA PRIMEIRO

## ⚠️ PROBLEMA IDENTIFICADO
A lógica atual verifica o bucket primeiro, mas uma tarefa NÃO PODE existir em buckets diferentes!

## ✅ NOVA LÓGICA CORRETA

```
1. Verificar se a TAREFA existe (em QUALQUER bucket)
   ├─ SE EXISTE → Não criar (ou atualizar bucket se mudou)
   └─ SE NÃO EXISTE → Verificar/Criar bucket → Criar tarefa
```

---

# 📋 ESTRUTURA REORGANIZADA DO FLUXO

## FLUXO PRINCIPAL:
```
1. Recorrência
    ↓
2. Obter_Dados_Excel
    ↓
3. Listar_Todos_Buckets
    ↓
4. Obter_Tarefas_Existentes
    ↓
5. Processar_Cada_Linha_Excel (ForEach)
    │
    ├─ PRIMEIRO: Verificar_Tarefa_Existe (GLOBAL)
    │
    ├─ Condição: Tarefa_Ja_Existe?
    │   │
    │   ├─ SIM (tarefa existe):
    │   │   ├─ Log: "Tarefa já existe"
    │   │   └─ (Opcional) Verificar se mudou de bucket
    │   │
    │   └─ NÃO (tarefa não existe):
    │       │
    │       ├─ Encontrar_Bucket_Correspondente
    │       │
    │       ├─ Bucket_Existe?
    │       │   ├─ NÃO → Criar_Novo_Bucket
    │       │   └─ SIM → Usar_Existente
    │       │
    │       └─ Criar_Nova_Tarefa_Planner
```

---

# 🔧 IMPLEMENTAÇÃO PASSO A PASSO

## PASSO 1: REORGANIZAR AS AÇÕES

### 1.1 - Mova "Verificar_Tarefa_Existe" para o INÍCIO
- Deve ser a PRIMEIRA ação dentro do loop
- ANTES de verificar bucket

### 1.2 - Configure "Verificar_Tarefa_Existe"
```json
{
  "type": "Query",
  "inputs": {
    "from": "@body('Obter_Tarefas_Existentes')?['value']",
    "where": "@equals(toLower(trim(item()?['title'])), toLower(trim(items('Processar_Cada_Linha_Excel')?['Nome da Tarefa'])))"
  }
}
```

## PASSO 2: CRIAR CONDIÇÃO PRINCIPAL

### 2.1 - Adicione condição "Tarefa_Ja_Existe"
```
Nome: Verificar_Se_Tarefa_Ja_Existe
Condição: length(body('Verificar_Tarefa_Existe')) é maior que 0
```

### 2.2 - No bloco "SIM" (Tarefa existe):
```json
{
  "Log_Tarefa_Duplicada": {
    "type": "Compose",
    "inputs": {
      "aviso": "TAREFA JÁ EXISTE - NÃO SERÁ CRIADA",
      "tarefa": "@items('Processar_Cada_Linha_Excel')?['Nome da Tarefa']",
      "tarefa_existente": "@first(body('Verificar_Tarefa_Existe'))",
      "bucket_atual": "@first(body('Verificar_Tarefa_Existe'))?['bucketId']",
      "bucket_solicitado": "@items('Processar_Cada_Linha_Excel')?['Bucket']"
    }
  }
}
```

### 2.3 - No bloco "NÃO" (Tarefa não existe):
Aqui vai TODA a lógica de bucket e criação

## PASSO 3: LÓGICA DO BUCKET (dentro do NÃO)

### 3.1 - Encontrar bucket
```json
{
  "Encontrar_Bucket_Correspondente": {
    "type": "Query",
    "inputs": {
      "from": "@body('Listar_Todos_Buckets')?['value']",
      "where": "@equals(toLower(trim(item()?['name'])), toLower(trim(items('Processar_Cada_Linha_Excel')?['Bucket'])))"
    }
  }
}
```

### 3.2 - Verificar se bucket existe
```json
{
  "Verificar_Se_Bucket_Existe": {
    "type": "If",
    "expression": {
      "equals": [
        "@length(body('Encontrar_Bucket_Correspondente'))",
        0
      ]
    },
    "actions": {
      // Criar bucket
    },
    "else": {
      // Usar existente
    }
  }
}
```

### 3.3 - Criar tarefa (após resolver bucket)
```json
{
  "Criar_Nova_Tarefa_Planner": {
    "type": "OpenApiConnection",
    "inputs": {
      // configurações da tarefa
    }
  }
}
```

---

# 🔄 OPCIONAL: ATUALIZAR BUCKET SE MUDOU

## Se quiser MOVER tarefas de bucket quando mudar no Excel:

### No bloco "SIM" da condição principal, adicione:

```json
{
  "Verificar_Se_Mudou_Bucket": {
    "type": "If",
    "expression": {
      "not": {
        "equals": [
          "@first(body('Verificar_Tarefa_Existe'))?['bucketId']",
          "@first(body('Encontrar_Bucket_Correspondente'))?['id']"
        ]
      }
    },
    "actions": {
      "Atualizar_Bucket_Tarefa": {
        "type": "OpenApiConnection",
        "inputs": {
          "parameters": {
            "id": "@first(body('Verificar_Tarefa_Existe'))?['id']",
            "body/bucketId": "@first(body('Encontrar_Bucket_Correspondente'))?['id']"
          },
          "host": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_planner",
            "connection": "shared_planner",
            "operationId": "UpdateTask_V2"
          }
        }
      },
      "Log_Tarefa_Movida": {
        "type": "Compose",
        "inputs": "Tarefa movida de bucket"
      }
    }
  }
}
```

---

# ✅ VANTAGENS DA NOVA LÓGICA

1. **Garante unicidade:** Uma tarefa NUNCA será duplicada
2. **Performance:** Se tarefa existe, para imediatamente (não verifica bucket)
3. **Flexibilidade:** Pode atualizar bucket se necessário
4. **Clareza:** Lógica mais simples e direta

---

# 📊 FLUXO DE DECISÃO

```
Para cada linha do Excel:
    │
    ├─ Tarefa já existe em QUALQUER bucket?
    │   │
    │   ├─ SIM → FIM (não cria duplicata)
    │   │   └─ (Opcional: mover de bucket)
    │   │
    │   └─ NÃO → Continua
    │       │
    │       ├─ Bucket existe?
    │       │   ├─ NÃO → Cria bucket
    │       │   └─ SIM → Usa existente
    │       │
    │       └─ Cria tarefa no bucket correto
```

---

# 🧪 CASOS DE TESTE

## Teste 1: Tarefa nova
- Excel: "Nova Tarefa" | "Bucket A"
- Planner: Não existe
- Resultado: ✅ Cria tarefa em "Bucket A"

## Teste 2: Tarefa duplicada mesmo bucket
- Excel: "Tarefa X" | "Bucket A"
- Planner: "Tarefa X" já em "Bucket A"
- Resultado: ❌ Não cria (já existe)

## Teste 3: Tarefa duplicada outro bucket
- Excel: "Tarefa Y" | "Bucket B"
- Planner: "Tarefa Y" já em "Bucket A"
- Resultado: ❌ Não cria (já existe em outro bucket)

## Teste 4: Tarefa nova, bucket novo
- Excel: "Tarefa Z" | "Bucket Novo"
- Planner: Tarefa não existe, bucket não existe
- Resultado: ✅ Cria bucket + cria tarefa

---

# ⚠️ PONTOS IMPORTANTES

1. **Títulos únicos:** O Planner permite títulos duplicados tecnicamente, mas sua lógica agora impede
2. **Case insensitive:** Usa toLower() para evitar "Tarefa" ≠ "tarefa"
3. **Trim:** Remove espaços para evitar "Tarefa " ≠ "Tarefa"
4. **Global:** Verifica em TODOS os buckets, não apenas no bucket alvo

---

# 💡 RECOMENDAÇÃO

Se você tem tarefas que PRECISAM mudar de bucket:
- Implemente a lógica de "Atualizar_Bucket_Tarefa"
- Adicione um campo no Excel como "Forcar_Atualizacao"
- Log todas as mudanças para auditoria