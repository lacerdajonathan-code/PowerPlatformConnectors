# 🖼️ GUIA VISUAL DAS CORREÇÕES - PASSO A PASSO

## 🎯 VISÃO GERAL: 5 CORREÇÕES NECESSÁRIAS

```
┌─────────────────────────────────────────┐
│  1️⃣ CONDIÇÃO - Lógica Invertida        │
│  2️⃣ FOR_EACH - Loop Aninhado Extra     │
│  3️⃣ VERIFICAR TAREFA - Sintaxe Errada  │
│  4️⃣ CRIAR TAREFA - Referências Erradas │
│  5️⃣ QUERIES - Outputs vs Body          │
└─────────────────────────────────────────┘
```

---

## 🔴 CORREÇÃO 1: CONDIÇÃO - LÓGICA INVERTIDA

### VISUALIZAÇÃO DO ERRO:
```
┌──────────────────────────────────────────┐
│         CONDIÇÃO (COMO ESTÁ)             │
├──────────────────────────────────────────┤
│ SE:                                      │
│   Tarefa NÃO existe (= 0) ✅            │
│              E                           │
│   Bucket NÃO existe (= 0) ❌            │
│                                          │
│ PROBLEMA: Vai tentar criar tarefa       │
│ sem ter bucket! VAI DAR ERRO!           │
└──────────────────────────────────────────┘
```

### COMO CORRIGIR NO POWER AUTOMATE:

#### 1. CLIQUE NA CONDIÇÃO:
```
[Verificar_Se_Deve_Criar_Tarefa] ← Clique aqui
         ↓
    [✏️ Editar]
```

#### 2. ENCONTRE A SEGUNDA LINHA:
```
┌─────────────────────────────────────┐
│ Condição 1: [...] é igual a 0  ✅  │
│     E                               │
│ Condição 2: [...] é igual a 0  ❌  │ ← MUDE ESTA!
└─────────────────────────────────────┘
```

#### 3. MUDE O OPERADOR:
```
Onde está:  [é igual a ▼]
Mude para:  [é maior que ▼]
```

### RESULTADO CORRETO:
```
┌──────────────────────────────────────────┐
│         CONDIÇÃO (CORRIGIDA)             │
├──────────────────────────────────────────┤
│ SE:                                      │
│   Tarefa NÃO existe (= 0) ✅            │
│              E                           │
│   Bucket FOI encontrado (> 0) ✅        │
│                                          │
│ AGORA SIM! Cria apenas quando deve!     │
└──────────────────────────────────────────┘
```

---

## 🔴 CORREÇÃO 2: REMOVER LOOP FOR_EACH EXTRA

### VISUALIZAÇÃO DO ERRO:
```
┌─────────────────────────────┐
│ Processar_Cada_Linha (Loop) │ ← Já está em loop
│  └─ Condição                │
│      └─ SIM                 │
│          └─ For_each ❌     │ ← LOOP DENTRO DE LOOP!
│              └─ Criar       │
└─────────────────────────────┘

PROBLEMA: 10 linhas × 10 = 100 tarefas criadas!
```

### COMO CORRIGIR:

#### 1. COPIE A AÇÃO DE CRIAR:
```
For_each
  └─ [Criar_Nova_Tarefa_Planner]
           ↓
     [...] → Copiar para área de transferência
```

#### 2. DELETE O FOR_EACH:
```
[For_each] 
     ↓
  [...] → Excluir
```

#### 3. COLE NO LUGAR CERTO:
```
SIM (agora vazio)
  └─ [+ Adicionar uma ação]
           ↓
      [Minha área de transferência]
           ↓
      [Criar_Nova_Tarefa_Planner]
```

### RESULTADO CORRETO:
```
┌─────────────────────────────┐
│ Processar_Cada_Linha (Loop) │
│  └─ Condição                │
│      └─ SIM                 │
│          └─ Criar ✅        │ ← DIRETO, SEM LOOP EXTRA!
└─────────────────────────────┘
```

---

## 🔴 CORREÇÃO 3: VERIFICAR_TAREFA_EXISTE

### VISUALIZAÇÃO DO ERRO:
```
CAMPO "ONDE" (ERRADO):
┌──────────────────────────────────┐
│ @equals(item(), item()?['Nome']) │
│         ↑                        │
│    Objeto inteiro != String     │
└──────────────────────────────────┘
```

### COMO CORRIGIR:

#### CAMPO "DE":
```
Clique no campo → Expressão
Digite: body('Obter_Tarefas_Existentes')?['value']
```

#### CAMPO "ONDE":
```
┌─────────────────────────────────────────┐
│ [item()?['title']] [é igual a] [Nome]  │
│       ↑                           ↑     │
│   Expressão                   Dinâmico  │
└─────────────────────────────────────────┘
```

---

## 🔴 CORREÇÃO 4: CRIAR_NOVA_TAREFA - CAMPOS

### MAPA DE CORREÇÕES:
```
┌────────────────────────────────────────────┐
│ Campo          │ Errado      │ Correto     │
├────────────────────────────────────────────┤
│ Título         │ item()?[]   │ items('Pro..')│
│ BucketId       │ "DrX2..."   │ first(body..)│
│ Data Início    │ For_each    │ items('Pro..')│
│ Data Fim       │ For_each    │ items('Pro..')│
└────────────────────────────────────────────┘
```

### CORREÇÃO DO BUCKETID (MAIS IMPORTANTE):
```
ERRADO:  "DrX2VINapUOvCWMVUo_OaWQAGf2h"
         ↑ ID fixo - sempre o mesmo bucket!

CORRETO: first(body('Encontrar_Bucket_Correspondente'))?['id']
         ↑ ID dinâmico - bucket correto!
```

---

## 🔴 CORREÇÃO 5: SINTAXE DAS QUERIES

### DIFERENÇA:
```
❌ EVITE:  @outputs('Nome_Acao')?['body/value']
✅ USE:    @body('Nome_Acao')?['value']
```

### ONDE CORRIGIR:
1. **Encontrar_Bucket_Correspondente** - Campo "De"
2. **Verificar_Tarefa_Existe** - Campo "De"

---

## ✅ ESTRUTURA FINAL CORRETA

```
📊 Obter_Dados_Excel
    ↓
🗂️ Listar_Todos_Buckets (1x só!)
    ↓
📋 Obter_Tarefas_Existentes (1x só!)
    ↓
🔄 Processar_Cada_Linha_Excel
    │
    ├─ 🔍 Encontrar_Bucket
    │   De: body('Listar_Todos_Buckets')?['value']
    │
    ├─ 🔎 Verificar_Tarefa
    │   De: body('Obter_Tarefas_Existentes')?['value']
    │   Onde: item()?['title'] = Nome
    │
    └─ ❓ Condição
        │ Tarefa não existe (=0) E Bucket existe (>0)
        │
        ├─ ✅ SIM → Criar_Tarefa (SEM LOOP!)
        │           BucketId: first(body(...))?['id']
        │
        └─ ❌ NÃO → Log
```

---

## 🧪 TESTE DE VALIDAÇÃO

### PLANILHA DE TESTE:
```
┌─────────────────┬──────────┬────────────┐
│ Nome da Tarefa  │ Bucket   │ Data       │
├─────────────────┼──────────┼────────────┤
│ Teste A         │ Bucket 1 │ 2024-01-20 │
│ Teste B         │ Bucket 2 │ 2024-01-21 │
└─────────────────┴──────────┴────────────┘
```

### RESULTADOS ESPERADOS:
```
1ª Execução: ✅ 2 tarefas criadas
2ª Execução: ✅ 0 tarefas (já existem)

Se criar 4+ tarefas: ❌ Ainda tem loop duplicado!
```

---

## 💡 DICA FINAL

### PARA VER O QUE ESTÁ ACONTECENDO:

Adicione uma ação "Compor" após cada etapa:
```
[Encontrar_Bucket]
    ↓
[➕ Nova etapa]
    ↓
[Compor]
  Entradas: body('Encontrar_Bucket_Correspondente')
```

Isso mostra o conteúdo durante a execução!