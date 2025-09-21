# 📚 GUIA COMPLETO DE CORREÇÃO - PASSO A PASSO NO POWER AUTOMATE

## 🎯 VISÃO GERAL DAS CORREÇÕES

Este guia mostra EXATAMENTE o que clicar e digitar em cada campo do Power Automate para corrigir seu fluxo.

---

## ⚙️ NÓ 1: TRIGGER - RECORRÊNCIA

### ✅ Este está CORRETO! Não precisa mudar nada.

**Localização:** Primeiro bloco do fluxo

**Configuração Atual (manter assim):**
- **Intervalo:** `1`
- **Frequência:** `Hora`
- **Fuso horário:** `E. South America Standard Time`

---

## 📊 NÓ 2: LISTAR LINHAS DO EXCEL

### ✅ Este está CORRETO! Mas vamos renomear para melhor organização.

**Como Renomear:**
1. Clique nos **3 pontinhos** no canto superior direito da ação
2. Selecione **Renomear**
3. Digite: `Obter_Dados_Excel`

**Campos (manter como estão):**
- **Localização:** `OneDrive for Business`
- **Biblioteca de Documentos:** `Documentos`
- **Arquivo:** `/1.Gerência/Controles/Planner_Tarefas_Unificadas.xlsx`
- **Tabela:** `{92AC1A55-2203-4675-8AEA-A904F23A71D8}`

---

## 🗂️ NÓ 3: LISTAR BUCKETS

### ❌ CORREÇÃO CRÍTICA: MOVER PARA FORA DO LOOP!

**PROBLEMA:** Está dentro do loop "Aplicar_a_cada"

**COMO CORRIGIR:**

### Passo 1: Deletar a ação atual
1. Encontre "Listar_buckets" DENTRO do loop
2. Clique nos **3 pontinhos**
3. Selecione **Excluir**

### Passo 2: Criar nova ação no lugar correto
1. Clique em **Nova etapa** logo APÓS "Obter_Dados_Excel"
2. Pesquise: `Planner`
3. Selecione: **Listar buckets**
4. Renomeie para: `Listar_Todos_Buckets`

### Passo 3: Configurar os campos
- **ID do Grupo:** `332dd89f-c104-4ae6-96a9-6a45b8ec6f6f`
- **ID do Plano:** `XLO7WAvmFEGU07P6t_UH4WQAF9gY`

---

## 📋 NÓ 4: LISTAR TAREFAS EXISTENTES

### ❌ CORREÇÃO: MOVER E RECONFIGURAR

**PROBLEMA:** Está dentro do loop e é executado múltiplas vezes

### Passo 1: Deletar a ação atual
1. Encontre "Listar_tarefas" dentro do loop
2. Clique nos **3 pontinhos** → **Excluir**

### Passo 2: Criar nova ação
1. Clique em **Nova etapa** após "Listar_Todos_Buckets"
2. Pesquise: `Planner`
3. Selecione: **Listar tarefas**
4. Renomeie para: `Obter_Tarefas_Existentes`

### Passo 3: Configurar campos
- **ID do Grupo:** `332dd89f-c104-4ae6-96a9-6a45b8ec6f6f`
- **ID do Plano:** `XLO7WAvmFEGU07P6t_UH4WQAF9gY`

---

## 🔄 NÓ 5: LOOP FOREACH (Aplicar a cada)

### ✅ MANTER, mas LIMPAR o conteúdo interno

### Passo 1: Renomear
1. Clique nos **3 pontinhos** do "Aplicar_a_cada"
2. **Renomear** para: `Processar_Cada_Linha_Excel`

### Passo 2: Verificar campo
- **Selecionar uma saída das etapas anteriores:** 
  - Deve mostrar: `value` de "Obter_Dados_Excel"
  - Se não, clique no campo e selecione: `body('Obter_Dados_Excel')?['value']`

---

## 🔍 NÓ 6: FILTRAR BUCKET (Dentro do Loop)

### ❌ CORREÇÃO COMPLETA NECESSÁRIA

**PROBLEMA:** Sintaxe incorreta no campo "De"

### Passo 1: Deletar "Filtrar_Matriz" atual
1. Clique nos **3 pontinhos** → **Excluir**

### Passo 2: Criar nova ação de filtro
1. Dentro do loop, clique **Nova etapa**
2. Pesquise: `Filtrar matriz`
3. Selecione a ação **Filtrar matriz** (Data Operations)
4. Renomeie para: `Encontrar_Bucket_Correspondente`

### Passo 3: Configurar campos
- **De:** Clique e selecione `value` de "Listar_Todos_Buckets"
  - Ou digite: `@body('Listar_Todos_Buckets')?['value']`
- **Onde:** 
  1. Campo esquerdo: `item()?['name']`
  2. Operador: `é igual a`
  3. Campo direito: Selecione `Bucket` do item atual
     - Expressão: `@items('Processar_Cada_Linha_Excel')?['Bucket']`

---

## 🔎 NÓ 7: VERIFICAR SE TAREFA EXISTE

### ❌ CRIAR NOVA AÇÃO

### Passo 1: Adicionar ação de filtro
1. Após "Encontrar_Bucket_Correspondente", clique **Nova etapa**
2. Pesquise: `Filtrar matriz`
3. Renomeie para: `Verificar_Tarefa_Existe`

### Passo 2: Configurar campos
- **De:** `value` de "Obter_Tarefas_Existentes"
  - Expressão: `@body('Obter_Tarefas_Existentes')?['value']`
- **Onde:**
  1. Campo esquerdo: `item()?['title']`
  2. Operador: `é igual a`
  3. Campo direito: `Nome da Tarefa` do item atual
     - Expressão: `@items('Processar_Cada_Linha_Excel')?['Nome da Tarefa']`

---

## ❓ NÓ 8: CONDIÇÃO

### ❌ CORREÇÃO COMPLETA DA LÓGICA

### Passo 1: Deletar condição atual
1. Clique nos **3 pontinhos** da "Condição" → **Excluir**

### Passo 2: Criar nova condição
1. Clique **Nova etapa**
2. Pesquise: `Condição`
3. Renomeie para: `Verificar_Se_Deve_Criar_Tarefa`

### Passo 3: Configurar a lógica (IMPORTANTE!)

**Clique em "Editar no modo avançado" e cole:**

```
@and(
    equals(length(body('Verificar_Tarefa_Existe')), 0),
    greater(length(body('Encontrar_Bucket_Correspondente')), 0)
)
```

**OU configure manualmente:**

1. **Primeira condição:**
   - Clique em **"Escolher um valor"**
   - Selecione **Expressão**
   - Digite: `length(body('Verificar_Tarefa_Existe'))`
   - Operador: **é igual a**
   - Valor: `0`

2. **Clique em "+ Adicionar" → "Adicionar linha"**

3. **Segunda condição:**
   - Relacionamento: **E**
   - Clique em **"Escolher um valor"**
   - Selecione **Expressão**
   - Digite: `length(body('Encontrar_Bucket_Correspondente'))`
   - Operador: **é maior que**
   - Valor: `0`

---

## ✅ NÓ 9: CRIAR TAREFA (Dentro do SIM da Condição)

### ❌ CORREÇÃO DO BUCKETID

### Passo 1: Adicionar ação no bloco "Sim"
1. No bloco **"Sim"** da condição, clique **Adicionar uma ação**
2. Pesquise: `Planner`
3. Selecione: **Criar uma tarefa**
4. Renomeie para: `Criar_Nova_Tarefa_Planner`

### Passo 2: Configurar TODOS os campos

#### Campos Obrigatórios:
- **ID do Grupo:** `332dd89f-c104-4ae6-96a9-6a45b8ec6f6f`
- **ID do Plano:** `XLO7WAvmFEGU07P6t_UH4WQAF9gY`
- **Título:** Selecione `Nome da Tarefa` do item atual
  - Expressão: `@items('Processar_Cada_Linha_Excel')?['Nome da Tarefa']`

#### Campo CRÍTICO (corrigir o erro):
- **ID do Bucket:** 
  1. Clique no campo
  2. Selecione **Expressão**
  3. Digite: `first(body('Encontrar_Bucket_Correspondente'))?['id']`
  4. ⚠️ NÃO use um ID fixo!

#### Campos Opcionais:
- **Data de início:** Selecione `Data de início` do Excel
  - Expressão: `@items('Processar_Cada_Linha_Excel')?['Data de início']`
- **Data de conclusão:** Selecione `Data de conclusão` do Excel
  - Expressão: `@items('Processar_Cada_Linha_Excel')?['Data de conclusão']`

---

## 🚫 NÓ 10: BLOCO "NÃO" DA CONDIÇÃO

### ✅ OPCIONAL - Adicionar Log

### Passo 1: No bloco "Não", adicionar ação
1. Clique **Adicionar uma ação**
2. Pesquise: `Compor`
3. Renomeie para: `Log_Tarefa_Ja_Existe`

### Passo 2: Configurar
- **Entradas:** Digite:
```
Tarefa já existe ou bucket não encontrado: @{items('Processar_Cada_Linha_Excel')?['Nome da Tarefa']}
```

---

## 🗑️ AÇÕES PARA DELETAR

### ❌ DELETAR COMPLETAMENTE:

1. **For_each** (loops aninhados no else)
2. **For_each_1** (loops aninhados)
3. **Compor** com `first(body('Filtrar_Matriz'))?['id']`
4. Qualquer ação duplicada de "Listar buckets" ou "Listar tarefas"

---

## 🎯 ESTRUTURA FINAL CORRETA

```
📍 Recorrência (Trigger)
    ↓
📊 Obter_Dados_Excel
    ↓
🗂️ Listar_Todos_Buckets
    ↓
📋 Obter_Tarefas_Existentes
    ↓
🔄 Processar_Cada_Linha_Excel (ForEach)
    ├─ 🔍 Encontrar_Bucket_Correspondente
    ├─ 🔎 Verificar_Tarefa_Existe
    └─ ❓ Verificar_Se_Deve_Criar_Tarefa (Condição)
        ├─ ✅ SIM → Criar_Nova_Tarefa_Planner
        └─ ❌ NÃO → Log_Tarefa_Ja_Existe
```

---

## ⚠️ CHECKLIST FINAL DE VALIDAÇÃO

Antes de salvar e testar, verifique:

- [ ] "Listar_Todos_Buckets" está FORA do loop
- [ ] "Obter_Tarefas_Existentes" está FORA do loop
- [ ] Não há loops For_each aninhados
- [ ] BucketId usa expressão dinâmica, não ID fixo
- [ ] A condição verifica 2 coisas com AND
- [ ] Todas as ações estão renomeadas para facilitar debug

---

## 🧪 COMO TESTAR

1. **Salve o fluxo**
2. Clique em **Testar** → **Manualmente**
3. Use uma planilha com apenas 2-3 linhas primeiro
4. Verifique o histórico de execução
5. Confirme no Planner se as tarefas foram criadas

---

## 💡 DICAS IMPORTANTES

1. **Use o modo "Peek code"** para ver/editar JSON diretamente
2. **Sempre teste com poucos dados** primeiro
3. **Monitore o consumo de API** no admin center
4. **Ative notificações de falha** nas configurações do fluxo
5. **Documente mudanças** no campo de descrição do fluxo