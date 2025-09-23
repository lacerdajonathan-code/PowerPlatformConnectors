# 🔧 GUIA DE CORREÇÃO CAMPO POR CAMPO - POWER AUTOMATE

## 📍 LOCALIZAÇÃO DOS ERROS NO SEU FLUXO

Seu fluxo tem a seguinte estrutura:
1. ✅ Recorrência (OK)
2. ✅ Obter_Dados_Excel (OK)
3. ✅ Listar_Todos_Buckets (OK)
4. ✅ Obter_Tarefas_Existentes (OK)
5. ⚠️ Processar_Cada_Linha_Excel (PRECISA CORREÇÕES)

---

# 🔴 CORREÇÃO 1: CONDIÇÃO COM LÓGICA INVERTIDA

## 📍 ONDE ENCONTRAR:
```
Processar_Cada_Linha_Excel 
  └─> Verificar_Se_Deve_Criar_Tarefa
      └─> Clique para expandir a condição
```

## 🎯 O QUE FAZER:

### PASSO 1: Abrir a Condição
1. Clique no bloco **"Verificar_Se_Deve_Criar_Tarefa"**
2. Clique no ícone de **lápis** (editar) no canto superior direito

### PASSO 2: Localizar a Segunda Condição
Você verá duas linhas de condição conectadas por "E":
```
Primeira linha:  length(...) é igual a 0  ✅ (ESTÁ CORRETA)
Segunda linha:   length(...) é igual a 0  ❌ (ESTÁ ERRADA)
```

### PASSO 3: Corrigir a Segunda Linha

#### MÉTODO A - Interface Visual:
1. Na **SEGUNDA linha** da condição
2. Onde está **"é igual a"**, clique na setinha
3. Mude para **"é maior que"**
4. O valor continua sendo **0**

#### MÉTODO B - Modo Avançado:
1. Clique em **"Editar no modo avançado"** (canto superior direito)
2. **LOCALIZE este trecho:**
```json
{
  "equals": [
    "@length(body('Encontrar_Bucket_Correspondente'))",
    0
  ]
}
```
3. **SUBSTITUA POR:**
```json
{
  "greater": [
    "@length(body('Encontrar_Bucket_Correspondente'))",
    0
  ]
}
```
4. Clique **OK**

### 📸 COMO DEVE FICAR:
```
SE:
✅ length(body('Verificar_Tarefa_Existe')) é igual a 0
    E
✅ length(body('Encontrar_Bucket_Correspondente')) é maior que 0
```

---

# 🔴 CORREÇÃO 2: REMOVER LOOP FOR_EACH ANINHADO

## 📍 ONDE ENCONTRAR:
```
Processar_Cada_Linha_Excel 
  └─> Verificar_Se_Deve_Criar_Tarefa
      └─> Bloco "Sim"
          └─> For_each  ❌ (ESTE DEVE SER DELETADO)
```

## 🎯 O QUE FAZER:

### PASSO 1: Salvar a Ação de Criar Tarefa
1. Expanda o bloco **"For_each"** dentro do "Sim"
2. Encontre **"Criar_Nova_Tarefa_Planner"**
3. Clique nos **3 pontinhos** (...) 
4. Selecione **"Copiar para minha área de transferência"**

### PASSO 2: Deletar o Loop For_each
1. Clique nos **3 pontinhos** do bloco **"For_each"**
2. Selecione **"Excluir"**
3. Confirme a exclusão

### PASSO 3: Colar a Ação no Lugar Correto
1. No bloco **"Sim"** (agora vazio)
2. Clique em **"Adicionar uma ação"**
3. Clique em **"Minha área de transferência"**
4. Selecione **"Criar_Nova_Tarefa_Planner"**

### ⚠️ IMPORTANTE:
A ação "Criar_Nova_Tarefa_Planner" deve estar DIRETAMENTE dentro do "Sim", sem nenhum loop ao redor!

---

# 🔴 CORREÇÃO 3: VERIFICAR_TAREFA_EXISTE - SINTAXE

## 📍 ONDE ENCONTRAR:
```
Processar_Cada_Linha_Excel 
  └─> Verificar_Tarefa_Existe
```

## 🎯 O QUE FAZER:

### PASSO 1: Abrir a Query
1. Clique em **"Verificar_Tarefa_Existe"**
2. Clique no ícone de **lápis** (editar)

### PASSO 2: Corrigir o Campo "De"
1. **Campo "De":**
   - Clique no campo
   - Delete o conteúdo atual
   - Clique em **"Expressão"**
   - Digite: `body('Obter_Tarefas_Existentes')?['value']`
   - Clique **OK**

### PASSO 3: Corrigir o Campo "Onde"
1. No campo **"Onde"**, você tem dois campos para preencher:

#### Campo da Esquerda:
- Clique no campo
- Selecione **"Expressão"**
- Digite: `item()?['title']`
- Clique **OK**

#### Campo do Meio (Operador):
- Selecione: **"é igual a"**

#### Campo da Direita:
- Clique no campo
- Na lista de conteúdo dinâmico, procure por **"Nome da Tarefa"**
- OU use Expressão: `items('Processar_Cada_Linha_Excel')?['Nome da Tarefa']`

### 📸 COMO DEVE FICAR:
```
De: body('Obter_Tarefas_Existentes')?['value']
Onde: item()?['title'] é igual a [Nome da Tarefa]
```

---

# 🔴 CORREÇÃO 4: CRIAR_NOVA_TAREFA - REFERÊNCIAS

## 📍 ONDE ENCONTRAR:
```
Processar_Cada_Linha_Excel 
  └─> Verificar_Se_Deve_Criar_Tarefa
      └─> Sim
          └─> Criar_Nova_Tarefa_Planner
```

## 🎯 O QUE FAZER:

### PASSO 1: Abrir a Ação
1. Clique em **"Criar_Nova_Tarefa_Planner"**
2. Clique no ícone de **lápis** (editar)

### PASSO 2: Corrigir CADA Campo

#### ✅ Campo "ID do Grupo":
- Deve estar: `332dd89f-c104-4ae6-96a9-6a45b8ec6f6f`
- Se não, copie e cole este valor

#### ✅ Campo "ID do Plano":
- Deve estar: `XLO7WAvmFEGU07P6t_UH4WQAF9gY`
- Se não, copie e cole este valor

#### 🔧 Campo "Título":
1. Delete o conteúdo atual
2. Na lista de conteúdo dinâmico, procure a seção **"Processar_Cada_Linha_Excel"**
3. Selecione **"Nome da Tarefa"**
4. OU use Expressão: `items('Processar_Cada_Linha_Excel')?['Nome da Tarefa']`

#### 🔧 Campo "ID do Bucket":
1. Delete o conteúdo atual
2. Clique em **"Expressão"**
3. Digite EXATAMENTE: `first(body('Encontrar_Bucket_Correspondente'))?['id']`
4. Clique **OK**

#### 🔧 Campo "Data de início":
1. Delete o conteúdo atual
2. Na lista dinâmica, seção **"Processar_Cada_Linha_Excel"**
3. Selecione **"Data de início"**
4. OU Expressão: `items('Processar_Cada_Linha_Excel')?['Data de início']`

#### 🔧 Campo "Data de conclusão":
1. Delete o conteúdo atual
2. Na lista dinâmica, seção **"Processar_Cada_Linha_Excel"**
3. Selecione **"Data de conclusão"**
4. OU Expressão: `items('Processar_Cada_Linha_Excel')?['Data de conclusão']`

---

# 🔴 CORREÇÃO 5: ENCONTRAR_BUCKET - SINTAXE

## 📍 ONDE ENCONTRAR:
```
Processar_Cada_Linha_Excel 
  └─> Encontrar_Bucket_Correspondente
```

## 🎯 O QUE FAZER:

### PASSO 1: Abrir a Query
1. Clique em **"Encontrar_Bucket_Correspondente"**
2. Clique no ícone de **lápis** (editar)

### PASSO 2: Corrigir o Campo "De"
1. Delete o conteúdo atual
2. Clique em **"Expressão"**
3. Digite: `body('Listar_Todos_Buckets')?['value']`
4. Clique **OK**

### PASSO 3: Verificar o Campo "Onde"
Deve estar assim:
- Esquerda: `item()?['name']`
- Operador: `é igual a`
- Direita: `[Bucket]` do Processar_Cada_Linha_Excel

---

# ✅ CHECKLIST DE VALIDAÇÃO FINAL

## Após todas as correções, verifique:

### 1️⃣ Na Condição:
- [ ] Primeira condição: `length(...) é igual a 0`
- [ ] Segunda condição: `length(...) é maior que 0` (NÃO "igual a")
- [ ] Operador entre elas: **E**

### 2️⃣ No bloco "Sim":
- [ ] NÃO tem nenhum "For_each"
- [ ] "Criar_Nova_Tarefa_Planner" está direto no "Sim"

### 3️⃣ Em Verificar_Tarefa_Existe:
- [ ] De: `body('Obter_Tarefas_Existentes')?['value']`
- [ ] Onde: `item()?['title']` é igual a `Nome da Tarefa`

### 4️⃣ Em Criar_Nova_Tarefa_Planner:
- [ ] Título usa: `items('Processar_Cada_Linha_Excel')`
- [ ] BucketId usa: `first(body('Encontrar_Bucket_Correspondente'))?['id']`
- [ ] Datas usam: `items('Processar_Cada_Linha_Excel')`

### 5️⃣ Em Encontrar_Bucket_Correspondente:
- [ ] De: `body('Listar_Todos_Buckets')?['value']`
- [ ] Onde: `item()?['name']` é igual a `Bucket`

---

# 🧪 TESTE RÁPIDO

## Crie uma planilha Excel de teste:

| Nome da Tarefa | Bucket      | Data de início | Data de conclusão |
|----------------|-------------|----------------|-------------------|
| Teste Correção 1 | Bucket A  | 2024-01-20     | 2024-01-25       |
| Teste Correção 2 | Bucket B  | 2024-01-21     | 2024-01-26       |

## Execute e verifique:
1. **Primeira execução:** Deve criar 2 tarefas
2. **Segunda execução:** Deve criar 0 tarefas (já existem)
3. **Se criar 4, 6 ou mais:** Ainda tem loop duplicado!

---

# 💡 DICAS EXTRAS

## Se algo não funcionar:

### 1. Use o Histórico de Execução:
- Vá em **"Histórico de execuções"**
- Clique na execução com falha
- Veja exatamente onde parou

### 2. Modo Debug:
- Adicione ações **"Compor"** entre as etapas
- Use para ver o conteúdo das variáveis

### 3. Teste com 1 linha só:
- Limite o Excel a 1 linha
- Mais fácil identificar problemas

---

# ⚠️ ERROS COMUNS E SOLUÇÕES

## Erro: "Cannot read property 'id' of null"
**Causa:** Bucket não encontrado
**Solução:** Verifique se o nome do bucket no Excel está EXATAMENTE igual ao Planner

## Erro: "The request is invalid"
**Causa:** Campos obrigatórios faltando
**Solução:** Verifique se Título e BucketId estão preenchidos

## Erro: "Too many requests"
**Causa:** Loop duplicado executando muitas vezes
**Solução:** Remova TODOS os For_each aninhados