# 🚀 GUIA COMPLETO - CRIAR BUCKETS AUTOMATICAMENTE NO PLANNER

## 📋 VISÃO GERAL DA SOLUÇÃO

Vamos implementar uma lógica que:
1. Verifica se o bucket existe
2. Se NÃO existir, cria automaticamente
3. Depois prossegue para criar a tarefa

---

# 🔧 PARTE 1: ADICIONAR CRIAÇÃO AUTOMÁTICA DE BUCKET

## 📍 ONDE ADICIONAR:
Logo APÓS "Encontrar_Bucket_Correspondente" e ANTES de "Verificar_Tarefa_Existe"

## PASSO 1: Adicionar Condição para Verificar Bucket

### 1.1 - Clique em "Nova etapa" após "Encontrar_Bucket_Correspondente"
### 1.2 - Pesquise por "Condição"
### 1.3 - Renomeie para: `Verificar_Se_Bucket_Existe`

## PASSO 2: Configurar a Condição

### 2.1 - Na condição, configure:
- **Campo da esquerda:** Clique e selecione "Expressão"
- **Digite:** `length(body('Encontrar_Bucket_Correspondente'))`
- **Operador:** `é igual a`
- **Campo da direita:** `0`

### 📊 Isso significa:
- **SE** bucket NÃO foi encontrado (length = 0)
- **ENTÃO** criar o bucket
- **SENÃO** continuar normalmente

## PASSO 3: No Bloco "SIM" (Bucket não existe)

### 3.1 - Adicionar ação "Criar Bucket"
1. No bloco **"Sim"**, clique em **"Adicionar uma ação"**
2. Pesquise: `Planner`
3. Selecione: **"Criar um bucket"**
4. Renomeie para: `Criar_Novo_Bucket`

### 3.2 - Configurar os campos:
- **ID do Plano:** `XLO7WAvmFEGU07P6t_UH4WQAF9gY`
- **Nome:** 
  - Clique no campo
  - Na lista dinâmica, procure **"Processar_Cada_Linha_Excel"**
  - Selecione **"Bucket"**
  - OU use expressão: `@items('Processar_Cada_Linha_Excel')?['Bucket']`

### 3.3 - Adicionar delay (IMPORTANTE!)
1. Ainda no bloco "Sim", após "Criar_Novo_Bucket"
2. Clique em **"Adicionar uma ação"**
3. Pesquise: `Atraso`
4. Selecione: **"Atraso"**
5. Configure: **2 segundos**
   - **Contagem:** `2`
   - **Unidade:** `Segundo`

> ⚠️ O delay é importante para dar tempo do bucket ser criado antes de usar

### 3.4 - Recarregar lista de buckets
1. Após o "Atraso", adicione nova ação
2. Pesquise: `Planner`
3. Selecione: **"Listar buckets"**
4. Renomeie para: `Listar_Buckets_Atualizado`
5. Configure:
   - **ID do Grupo:** `332dd89f-c104-4ae6-96a9-6a45b8ec6f6f`
   - **ID do Plano:** `XLO7WAvmFEGU07P6t_UH4WQAF9gY`

### 3.5 - Encontrar o bucket recém-criado
1. Adicione nova ação após "Listar_Buckets_Atualizado"
2. Pesquise: `Filtrar matriz`
3. Renomeie para: `Encontrar_Bucket_Criado`
4. Configure:
   - **De:** `body('Listar_Buckets_Atualizado')?['value']`
   - **Onde:** 
     - Esquerda: `item()?['name']`
     - Operador: `é igual a`
     - Direita: Selecione **"Bucket"** de Processar_Cada_Linha_Excel

### 3.6 - Atualizar variável do bucket
1. Adicione ação "Compor"
2. Renomeie para: `Definir_Bucket_Final`
3. No campo **Entradas:**
   - Expressão: `first(body('Encontrar_Bucket_Criado'))`

## PASSO 4: No Bloco "NÃO" (Bucket já existe)

### 4.1 - Adicionar ação para manter o bucket encontrado
1. No bloco **"Não"**, adicione ação **"Compor"**
2. Renomeie para: `Usar_Bucket_Existente`
3. No campo **Entradas:**
   - Expressão: `first(body('Encontrar_Bucket_Correspondente'))`

---

# 🔧 PARTE 2: AJUSTAR A LÓGICA PRINCIPAL

## PASSO 5: Modificar "Verificar_Se_Deve_Criar_Tarefa"

### 5.1 - Mover para DEPOIS da condição do bucket
1. Arraste "Verificar_Tarefa_Existe" para APÓS "Verificar_Se_Bucket_Existe"
2. Arraste "Verificar_Se_Deve_Criar_Tarefa" para APÓS "Verificar_Tarefa_Existe"

### 5.2 - Atualizar a condição principal
A condição agora deve verificar:
```
SE:
  length(body('Verificar_Tarefa_Existe')) é igual a 0
```
> Não precisa mais verificar o bucket, pois agora sempre existirá!

### 5.3 - Atualizar o BucketId em "Criar_Nova_Tarefa_Planner"
**MUDE DE:**
```
@first(body('Encontrar_Bucket_Correspondente'))?['id']
```

**PARA:**
```
@coalesce(outputs('Definir_Bucket_Final')?['id'], outputs('Usar_Bucket_Existente')?['id'])
```

---

# 🔧 PARTE 3: CORRIGIR DATAS DO EXCEL

## PASSO 6: Ajustar campos de data

### Em "Criar_Nova_Tarefa_Planner", ajuste:

### 6.1 - Campo "Data de início":
```
@if(
  empty(items('Processar_Cada_Linha_Excel')?['Data de início']),
  null,
  if(
    greater(int(items('Processar_Cada_Linha_Excel')?['Data de início']), 60000),
    null,
    addDays('1899-12-30', int(items('Processar_Cada_Linha_Excel')?['Data de início']))
  )
)
```

### 6.2 - Campo "Data de conclusão":
```
@if(
  empty(items('Processar_Cada_Linha_Excel')?['Data de conclusão']),
  null,
  if(
    greater(int(items('Processar_Cada_Linha_Excel')?['Data de conclusão']), 60000),
    null,
    addDays('1899-12-30', int(items('Processar_Cada_Linha_Excel')?['Data de conclusão']))
  )
)
```

---

# 📊 ESTRUTURA FINAL DO FLUXO

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
    ├─ Encontrar_Bucket_Correspondente
    │
    ├─ Verificar_Se_Bucket_Existe (Condição)
    │   ├─ SIM (não existe):
    │   │   ├─ Criar_Novo_Bucket
    │   │   ├─ Atraso (2 segundos)
    │   │   ├─ Listar_Buckets_Atualizado
    │   │   ├─ Encontrar_Bucket_Criado
    │   │   └─ Definir_Bucket_Final
    │   │
    │   └─ NÃO (existe):
    │       └─ Usar_Bucket_Existente
    │
    ├─ Verificar_Tarefa_Existe
    │
    └─ Verificar_Se_Deve_Criar_Tarefa (Condição)
        ├─ SIM: Criar_Nova_Tarefa_Planner
        └─ NÃO: Log_Tarefa_Ja_Existe
```

---

# 🐛 PARTE 4: ADICIONAR DEBUG E LOGS

## PASSO 7: Adicionar logs informativos

### 7.1 - Log quando criar bucket
No bloco "Sim" de "Verificar_Se_Bucket_Existe", após criar:
```json
{
  "type": "Compose",
  "inputs": {
    "acao": "Bucket criado",
    "nome": "@items('Processar_Cada_Linha_Excel')?['Bucket']",
    "id": "@outputs('Criar_Novo_Bucket')?['body/id']"
  }
}
```

### 7.2 - Log final de execução
Após "Verificar_Se_Deve_Criar_Tarefa":
```json
{
  "type": "Compose",
  "inputs": {
    "linha_processada": "@items('Processar_Cada_Linha_Excel')?['Nome da Tarefa']",
    "bucket": "@items('Processar_Cada_Linha_Excel')?['Bucket']",
    "bucket_criado": "@equals(length(body('Encontrar_Bucket_Correspondente')), 0)",
    "tarefa_criada": "@equals(length(body('Verificar_Tarefa_Existe')), 0)"
  }
}
```

---

# ✅ CHECKLIST DE VALIDAÇÃO

Antes de testar, confirme:

- [ ] Condição "Verificar_Se_Bucket_Existe" está APÓS "Encontrar_Bucket_Correspondente"
- [ ] Ação "Criar_Novo_Bucket" está no bloco "Sim"
- [ ] Tem um "Atraso" de 2 segundos após criar
- [ ] "Listar_Buckets_Atualizado" recarrega a lista
- [ ] BucketId usa `coalesce()` para pegar o bucket correto
- [ ] Datas usam a fórmula de conversão do Excel
- [ ] "Verificar_Tarefa_Existe" está APÓS a lógica do bucket

---

# 🧪 TESTE

## Planilha de teste:

| Nome da Tarefa | Bucket | Data de início | Data de conclusão |
|----------------|--------|----------------|-------------------|
| Teste Bucket Novo | Bucket Teste 123 | 45290 | 45297 |
| Teste Bucket Existente | To Do | 45291 | 45298 |

## Resultado esperado:
1. **Primeira linha:** Cria bucket "Bucket Teste 123" e depois a tarefa
2. **Segunda linha:** Usa bucket "To Do" existente e cria a tarefa
3. **Segunda execução:** Não cria nada (tarefas já existem)

---

# ⚠️ TRATAMENTO DE ERROS

## Se der erro ao criar bucket:

### Adicione validação do nome:
```json
{
  "type": "If",
  "expression": {
    "and": [
      {
        "not": {
          "equals": ["@items('Processar_Cada_Linha_Excel')?['Bucket']", ""]
        }
      },
      {
        "less": ["@length(items('Processar_Cada_Linha_Excel')?['Bucket'])", 100]
      }
    ]
  }
}
```

Isso garante que o nome do bucket:
- Não está vazio
- Tem menos de 100 caracteres

---

# 💡 DICAS FINAIS

1. **Buckets duplicados:** O Planner permite buckets com mesmo nome, então cuidado
2. **Limite de buckets:** Máximo ~200 buckets por plano
3. **Caracteres especiais:** Evite / \ : * ? " < > | no nome do bucket
4. **Performance:** Criar muitos buckets pode deixar o Planner lento

**Siga este guia passo a passo e seu fluxo criará buckets automaticamente!**