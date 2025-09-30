# Tutorial Completo: Correções Passo a Passo no Power Automate

## 📑 Índice
- [Correção #1: Nomear o ForEach](#correção-1-nomear-o-foreach)
- [Correção #2: Adicionar runAfter na primeira ação](#correção-2-adicionar-runafter-na-primeira-ação)
- [Correção #3: Adicionar tratamento de erros](#correção-3-adicionar-tratamento-de-erros)
- [Correção #4: Validar dados antes de processar](#correção-4-validar-dados-antes-de-processar)
- [Correção #5: Habilitar concorrência](#correção-5-habilitar-concorrência)
- [Correção #6: Verificar Excel vazio](#correção-6-verificar-excel-vazio)
- [Correção #7: Melhorar logging](#correção-7-melhorar-logging)
- [Correção #8: Tratar erro na criação de tarefa](#correção-8-tratar-erro-na-criação-de-tarefa)

---

# 🔴 CORREÇÕES CRÍTICAS

## Correção #1: Nomear o ForEach

### ❓ Por que fazer?
O código usa `items('Processar_Cada_Linha_Excel')`, mas o ForEach precisa ter esse nome explícito, senão o fluxo falha.

### 📍 Onde está o problema?
No loop ForEach que processa as linhas do Excel.

### ✅ Solução no Designer (Visual)

#### Passo 1: Abrir o fluxo
1. Vá para **Power Automate** (https://make.powerautomate.com)
2. Clique em **Meus fluxos**
3. Encontre seu fluxo
4. Clique em **Editar**

#### Passo 2: Localizar o ForEach
1. Role a tela até encontrar o bloco **"Apply to each"** (ForEach)
2. É o bloco que tem múltiplas ações dentro dele

#### Passo 3: Verificar/Alterar o nome
1. Clique nos **três pontos (...)** no canto superior direito do "Apply to each"
2. Selecione **"Rename"** (Renomear)
3. Digite exatamente: `Processar_Cada_Linha_Excel`
4. Clique em **OK**

![Ilustração conceitual]
```
┌─────────────────────────────────────┐
│ Apply to each              [...]    │ ← Clique nos 3 pontos
│                                     │
│ Select an output from previous      │
│ steps: value                        │
│                                     │
│ ┌─────────────────────────────┐   │
│ │ [Ações internas]             │   │
│ └─────────────────────────────┘   │
└─────────────────────────────────────┘

Opções que aparecem:
├─ Rename                    ← SELECIONE ESTA
├─ Settings
├─ Delete
└─ Copy to my clipboard
```

### ✅ Solução no Modo Código

#### Passo 1: Entrar no modo código
1. No editor do fluxo, clique em **"Peek code"** (ícone `</>`) no canto superior direito
2. Ou clique nos **três pontos (...)** do fluxo → **"Export"** → **"Package (.zip)"**

#### Passo 2: Localizar o ForEach no JSON
Procure por:
```json
{
  "type": "Foreach",
  "foreach": "@body('Obter_Dados_Excel')?['value']",
```

#### Passo 3: Adicionar/verificar o nome
O JSON deve estar assim (com o nome da ação sendo a chave do objeto):

```json
"Processar_Cada_Linha_Excel": {
  "type": "Foreach",
  "foreach": "@body('Obter_Dados_Excel')?['value']",
  "actions": {
    ...
  },
  "runAfter": {
    "Obter_Tarefas_Existentes": [
      "Succeeded"
    ]
  }
}
```

**IMPORTANTE**: No JSON do Power Automate, o nome da ação é a **chave do objeto**, não uma propriedade interna.

---

## Correção #2: Adicionar runAfter na primeira ação

### ❓ Por que fazer?
Toda ação dentro do ForEach precisa definir quando executar. A primeira ação precisa ter `"runAfter": {}` (vazio = executa imediatamente).

### 📍 Onde está o problema?
Na ação `Encontrar_Bucket_Correspondente` (primeira ação dentro do ForEach).

### ✅ Solução no Designer (Visual)

#### Método: Reorganizar as ações

**Nota**: No designer visual, o Power Automate geralmente adiciona `runAfter` automaticamente, mas pode haver casos onde não está correto.

#### Passo 1: Verificar a ordem
1. Abra o ForEach
2. Veja a ordem das ações dentro dele
3. A sequência deve ser:
   - `Encontrar_Bucket_Correspondente` (primeira)
   - `Verificar_Tarefa_Existe` (após a anterior)
   - `Debug_Verificar_Logica` (após a anterior)
   - `Verificar_Se_Deve_Criar_Tarefa` (após a anterior)

#### Passo 2: Se estiver fora de ordem
1. **DICA**: Você pode recriar as ações na ordem correta
2. Ou use o modo código (mais confiável)

### ✅ Solução no Modo Código (RECOMENDADO)

#### Passo 1: Localizar a primeira ação do ForEach
Dentro do `"actions": { ... }` do ForEach, encontre:

```json
"Encontrar_Bucket_Correspondente": {
  "type": "Query",
  "inputs": {
    "from": "@body('Listar_Todos_Buckets')?['value']",
    "where": "@equals(item()?['name'],items('Processar_Cada_Linha_Excel')?['Bucket'])"
  }
  // ❌ FALTA: "runAfter": {}
}
```

#### Passo 2: Adicionar runAfter vazio
Adicione a linha `"runAfter": {}` **ANTES** do fechamento da ação:

```json
"Encontrar_Bucket_Correspondente": {
  "type": "Query",
  "inputs": {
    "from": "@body('Listar_Todos_Buckets')?['value']",
    "where": "@equals(item()?['name'],items('Processar_Cada_Linha_Excel')?['Bucket'])"
  },
  "runAfter": {}  // ✅ ADICIONE ESTA LINHA
}
```

**ATENÇÃO**: Coloque uma **vírgula** depois do `}` do `inputs` e **antes** do `"runAfter"`.

#### Exemplo completo com contexto:
```json
"Processar_Cada_Linha_Excel": {
  "type": "Foreach",
  "foreach": "@body('Obter_Dados_Excel')?['value']",
  "actions": {
    "Encontrar_Bucket_Correspondente": {
      "type": "Query",
      "inputs": {
        "from": "@body('Listar_Todos_Buckets')?['value']",
        "where": "@equals(item()?['name'],items('Processar_Cada_Linha_Excel')?['Bucket'])"
      },
      "runAfter": {}  // ✅ ESTA LINHA
    },
    "Verificar_Tarefa_Existe": {
      "type": "Query",
      "inputs": {
        "from": "@body('Obter_Tarefas_Existentes')?['value']",
        "where": "@equals(item()?['title'],items('Processar_Cada_Linha_Excel')?['Nome da Tarefa'])"
      },
      "runAfter": {
        "Encontrar_Bucket_Correspondente": [
          "Succeeded"
        ]
      }
    },
    // ... outras ações
  }
}
```

---

# 🟡 CORREÇÕES IMPORTANTES

## Correção #3: Adicionar tratamento de erros

### ❓ Por que fazer?
Se alguma ação falhar (ex: Excel inacessível), o fluxo para sem avisar. Com tratamento de erro, você pode logar o problema ou enviar notificação.

### 📍 Onde adicionar?
Após ações críticas:
- `Obter_Dados_Excel`
- `Listar_Todos_Buckets`
- `Obter_Tarefas_Existentes`

### ✅ Solução no Designer (Visual)

#### Passo 1: Adicionar ação que trata erro
1. Clique no **[+]** após a ação `Obter_Dados_Excel`
2. Selecione **"Add a parallel branch"** (Adicionar ramificação paralela)

#### Passo 2: Configurar para executar em caso de falha
1. Clique nos **três pontos (...)** da NOVA ação que você acabou de adicionar
2. Selecione **"Configure run after"**
3. **Desmarque** ☑ "is successful"
4. **Marque** ☑ "has failed"
5. **Marque** ☑ "has timed out"
6. Clique em **Done**

```
Configuração "Configure run after":
□ is successful      ← Desmarque
☑ has failed         ← Marque
□ is skipped         ← Deixe desmarcado
☑ has timed out      ← Marque
```

#### Passo 3: Adicionar ação de tratamento
1. Na nova ação criada, escolha **"Compose"** ou **"Send an email"**
2. Se escolher Compose:
   - **Inputs**: 
   ```
   ERRO: Falha ao obter dados do Excel
   Timestamp: @{utcNow()}
   Detalhes: @{body('Obter_Dados_Excel')}
   ```

#### Exemplo visual da estrutura:
```
┌────────────────────────────┐
│ Obter_Dados_Excel          │
└──────────┬─────────────────┘
           │
           ├─ Succeeded → ┌─────────────────────┐
           │              │ Listar_Todos_Buckets│
           │              └─────────────────────┘
           │
           └─ Failed/TimedOut → ┌──────────────────────┐
                                │ Tratar_Erro_Excel     │
                                │ (Compose ou Email)   │
                                └──────────────────────┘
```

### ✅ Solução no Modo Código

#### Adicione esta ação no mesmo nível que outras ações principais:

```json
"Tratar_Erro_Excel": {
  "type": "Compose",
  "inputs": {
    "Status": "Erro crítico",
    "Motivo": "Falha ao obter dados do Excel",
    "Timestamp": "@utcNow()",
    "Detalhes": "@body('Obter_Dados_Excel')"
  },
  "runAfter": {
    "Obter_Dados_Excel": [
      "Failed",
      "TimedOut"
    ]
  }
}
```

**Onde colocar**: No objeto `"actions"` principal (não dentro do ForEach), no mesmo nível que `Obter_Dados_Excel`, `Listar_Todos_Buckets`, etc.

#### Para enviar email em vez de Compose:
```json
"Enviar_Email_Erro_Excel": {
  "type": "OpenApiConnection",
  "inputs": {
    "host": {
      "apiId": "/providers/Microsoft.PowerApps/apis/shared_office365",
      "connectionName": "shared_office365",
      "operationId": "SendEmailV2"
    },
    "parameters": {
      "emailMessage/To": "seu-email@petrobras.com.br",
      "emailMessage/Subject": "Erro no Fluxo Excel → Planner",
      "emailMessage/Body": "<p>Falha ao obter dados do Excel às @{utcNow()}</p>"
    }
  },
  "runAfter": {
    "Obter_Dados_Excel": [
      "Failed",
      "TimedOut"
    ]
  }
}
```

---

## Correção #4: Validar dados antes de processar

### ❓ Por que fazer?
Evita tentar criar tarefas com nomes vazios ou null, o que causaria erro.

### 📍 Onde adicionar?
Como primeira ação dentro do ForEach, antes de buscar bucket.

### ✅ Solução no Designer (Visual)

#### Passo 1: Adicionar Condition
1. Dentro do ForEach `Processar_Cada_Linha_Excel`
2. No início, ANTES de `Encontrar_Bucket_Correspondente`
3. Clique em **"+ New step"**
4. Procure por **"Condition"** e selecione

#### Passo 2: Configurar a primeira condição
1. No campo da esquerda, use **Dynamic content**
2. Procure e selecione: **Current item** → **Nome da Tarefa**
3. No meio, selecione: **"is not equal to"**
4. No campo da direita, deixe vazio (ou digite duas aspas vazias: `""`)

#### Passo 3: Adicionar segunda condição (AND)
1. Clique em **"Add"** → **"Add row"** (para adicionar condição AND)
2. Campo da esquerda: **Current item** → **Bucket**
3. No meio: **"is not equal to"**
4. No campo da direita: deixe vazio

#### Passo 4: Modo avançado (mais preciso)
Clique em **"Edit in advanced mode"** e cole esta expressão:

```javascript
and(
  not(equals(coalesce(items('Processar_Cada_Linha_Excel')?['Nome da Tarefa'], ''), '')),
  not(equals(coalesce(items('Processar_Cada_Linha_Excel')?['Bucket'], ''))
)
```

**Explicação**:
- `coalesce(valor, '')` → Se valor for null, retorna string vazia
- `not(equals(..., ''))` → Verifica que NÃO está vazio
- `and(...)` → Ambas condições devem ser verdadeiras

#### Passo 5: Mover ações existentes para dentro do "If yes"
1. As ações existentes (`Encontrar_Bucket_Correspondente`, etc.) devem ir dentro do **"If yes"**
2. ARRASTAR e SOLTAR cada ação para dentro
3. Ou RECORTAR (Ctrl+X) e COLAR (Ctrl+V) dentro do "If yes"

#### Passo 6: Adicionar ação no "If no"
1. No lado **"If no"**, clique **"Add an action"**
2. Escolha **"Compose"**
3. **Inputs**:
```
Dados inválidos - Nome da tarefa ou bucket vazio
Linha: @{items('Processar_Cada_Linha_Excel')}
```

### ✅ Solução no Modo Código

#### Estrutura completa:

```json
"Processar_Cada_Linha_Excel": {
  "type": "Foreach",
  "foreach": "@body('Obter_Dados_Excel')?['value']",
  "actions": {
    "Validar_Dados_Linha": {
      "type": "If",
      "expression": {
        "and": [
          {
            "not": {
              "equals": [
                "@coalesce(items('Processar_Cada_Linha_Excel')?['Nome da Tarefa'], '')",
                ""
              ]
            }
          },
          {
            "not": {
              "equals": [
                "@coalesce(items('Processar_Cada_Linha_Excel')?['Bucket'], '')",
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
            "where": "@equals(item()?['name'], items('Processar_Cada_Linha_Excel')?['Bucket'])"
          },
          "runAfter": {}
        },
        "Verificar_Tarefa_Existe": {
          "type": "Query",
          "inputs": {
            "from": "@body('Obter_Tarefas_Existentes')?['value']",
            "where": "@equals(item()?['title'], items('Processar_Cada_Linha_Excel')?['Nome da Tarefa'])"
          },
          "runAfter": {
            "Encontrar_Bucket_Correspondente": ["Succeeded"]
          }
        },
        // ... outras ações existentes vão aqui
      },
      "else": {
        "actions": {
          "Log_Dados_Invalidos": {
            "type": "Compose",
            "inputs": {
              "Status": "Dados inválidos",
              "Motivo": "Nome da tarefa ou bucket vazio",
              "Linha": "@items('Processar_Cada_Linha_Excel')",
              "Timestamp": "@utcNow()"
            },
            "runAfter": {}
          }
        }
      },
      "runAfter": {}
    }
  },
  "runAfter": {
    "Obter_Tarefas_Existentes": ["Succeeded"]
  }
}
```

---

## Correção #5: Habilitar concorrência

### ❓ Por que fazer?
Por padrão, o ForEach processa uma linha por vez (sequencial). Com concorrência, processa várias linhas ao mesmo tempo (muito mais rápido).

### 📍 Onde configurar?
No ForEach `Processar_Cada_Linha_Excel`.

### ✅ Solução no Designer (Visual)

#### Passo 1: Abrir configurações do ForEach
1. Clique nos **três pontos (...)** no canto superior direito do "Apply to each"
2. Selecione **"Settings"**

#### Passo 2: Ativar controle de concorrência
1. Procure a opção **"Concurrency Control"**
2. Mude o toggle de **OFF** para **ON**

```
Concurrency Control
○ OFF  ● ON          ← Clique aqui para ativar
```

#### Passo 3: Definir grau de paralelismo
1. Um slider aparece: **"Degree of Parallelism"**
2. Mova o slider para **20** (ou valor desejado)
3. Range: 1 (sequencial) até 50 (máximo paralelismo)

```
Degree of Parallelism
1 ──────●────────── 50
        20
```

**Recomendações**:
- **5-10**: Para testar inicialmente
- **20**: Bom equilíbrio (recomendado)
- **50**: Se tiver muitos dados e APIs aguentarem

#### Passo 4: Salvar
1. Clique em **"Done"**
2. Salve o fluxo

### ✅ Solução no Modo Código

Adicione dentro do objeto do ForEach:

```json
"Processar_Cada_Linha_Excel": {
  "type": "Foreach",
  "foreach": "@body('Obter_Dados_Excel')?['value']",
  "runtimeConfiguration": {
    "concurrency": {
      "repetitions": 20
    }
  },
  "actions": {
    // ... ações aqui
  },
  "runAfter": {
    "Obter_Tarefas_Existentes": ["Succeeded"]
  }
}
```

**Onde adicionar**: Imediatamente após a linha `"foreach"`, antes de `"actions"`.

### ⚠️ Cuidados ao usar concorrência:

1. **Rate limits**: APIs têm limites. Se houver muitos erros "429 Too Many Requests", reduza o valor
2. **Dependências**: Se as iterações dependem umas das outras, NÃO use concorrência
3. **Logs**: Logs ficarão intercalados (não em ordem sequencial)

---

## Correção #6: Verificar Excel vazio

### ❓ Por que fazer?
Se a tabela Excel estiver vazia, não há necessidade de executar as ações seguintes (economiza tempo e recursos).

### 📍 Onde adicionar?
Entre `Obter_Dados_Excel` e `Listar_Todos_Buckets`.

### ✅ Solução no Designer (Visual)

#### Passo 1: Adicionar Condition
1. Clique no **[+]** entre `Obter_Dados_Excel` e `Listar_Todos_Buckets`
2. Escolha **"Add an action"**
3. Procure por **"Condition"** e selecione

#### Passo 2: Configurar condição
1. Campo da esquerda: Clique em **Expression** (não Dynamic content)
2. Cole esta expressão:
```javascript
length(body('Obter_Dados_Excel')?['value'])
```
3. No meio: selecione **"is greater than"**
4. Campo da direita: digite **0**

```
┌──────────────────────────────────────────────┐
│ Condition                                    │
├──────────────────────────────────────────────┤
│ length(body('Obter_Dados_Excel')?['value'])  │
│ is greater than                              │
│ 0                                            │
└──────────────────────────────────────────────┘
```

#### Passo 3: Mover ações existentes para "If yes"
1. TODAS as ações após `Obter_Dados_Excel` devem ir para dentro do **"If yes"**:
   - `Listar_Todos_Buckets`
   - `Obter_Tarefas_Existentes`
   - `Processar_Cada_Linha_Excel` (o ForEach inteiro)

2. **Como mover** (2 opções):
   
   **Opção A - Recortar e colar**:
   - Clique nos **três pontos (...)** de cada ação
   - Escolha **"Delete"** (ela some temporariamente)
   - Dentro do "If yes", clique **"Add an action"**
   - Use **"My clipboard"** para colar a ação

   **Opção B - Recriar** (mais trabalhoso):
   - Adicione novamente cada ação dentro do "If yes"
   - Configure-as novamente

#### Passo 4: Adicionar ação no "If no"
1. No lado **"If no"**, clique **"Add an action"**
2. Escolha **"Compose"**
3. **Inputs**:
```
Nenhum dado para processar - A tabela Excel está vazia
Timestamp: @{utcNow()}
```

### ✅ Solução no Modo Código

Envolva as ações existentes em uma condição:

```json
"Verificar_Excel_Com_Dados": {
  "type": "If",
  "expression": {
    "greater": [
      "@length(body('Obter_Dados_Excel')?['value'])",
      0
    ]
  },
  "actions": {
    "Listar_Todos_Buckets": {
      // ... configuração existente
      "runAfter": {}
    },
    "Obter_Tarefas_Existentes": {
      // ... configuração existente
      "runAfter": {
        "Listar_Todos_Buckets": ["Succeeded"]
      }
    },
    "Processar_Cada_Linha_Excel": {
      // ... configuração existente (ForEach inteiro)
      "runAfter": {
        "Obter_Tarefas_Existentes": ["Succeeded"]
      }
    }
  },
  "else": {
    "actions": {
      "Log_Excel_Vazio": {
        "type": "Compose",
        "inputs": {
          "Status": "Nenhum dado para processar",
          "Mensagem": "A tabela do Excel está vazia ou não retornou dados",
          "Timestamp": "@utcNow()"
        },
        "runAfter": {}
      }
    }
  },
  "runAfter": {
    "Obter_Dados_Excel": ["Succeeded"]
  }
}
```

**Estrutura visual**:
```
Obter_Dados_Excel
       ↓
Verificar_Excel_Com_Dados (Condition)
       ├─ If yes → Listar_Todos_Buckets
       │              ↓
       │           Obter_Tarefas_Existentes
       │              ↓
       │           Processar_Cada_Linha_Excel
       │
       └─ If no  → Log_Excel_Vazio
```

---

## Correção #7: Melhorar logging

### ❓ Por que fazer?
O debug genérico sempre ativo polui os logs e pode impactar performance. Logs específicos por cenário são mais úteis.

### 📍 Onde modificar?
- Remover ou condicionar `Debug_Verificar_Logica`
- Adicionar logs específicos em cada cenário

### ✅ Solução no Designer (Visual)

#### Opção A: Remover Debug existente

1. Localize a ação `Debug_Verificar_Logica`
2. Clique nos **três pontos (...)**
3. Escolha **"Delete"**
4. Confirme

#### Opção B: Tornar Debug condicional

1. Crie uma **variável** no início do fluxo chamada `ModoDebug` (tipo Boolean, valor: false)
2. Envolva `Debug_Verificar_Logica` em uma **Condition**:
   - Se `ModoDebug` = true → executa debug
   - Se `ModoDebug` = false → pula

#### Adicionar logs específicos:

**Log 1: Tarefa criada com sucesso**
1. Após `Criar_Nova_Tarefa_Planner`, adicione **"Compose"**
2. Nomeie: `Log_Tarefa_Criada`
3. **Inputs**:
```json
{
  "Status": "Criada",
  "Tarefa": "@{items('Processar_Cada_Linha_Excel')?['Nome da Tarefa']}",
  "Bucket": "@{items('Processar_Cada_Linha_Excel')?['Bucket']}",
  "Timestamp": "@{utcNow()}"
}
```

**Log 2: Tarefa já existe**
1. No "If no" de `Verificar_Se_Deve_Criar_Tarefa`
2. Substitua/renomeie a ação existente
3. Nomeie: `Log_Tarefa_Ignorada`
4. **Inputs**:
```json
{
  "Status": "Ignorada",
  "Motivo": "@{if(greater(length(body('Verificar_Tarefa_Existe')), 0), 'Tarefa já existe', 'Bucket não encontrado')}",
  "Tarefa": "@{items('Processar_Cada_Linha_Excel')?['Nome da Tarefa']}",
  "Bucket": "@{items('Processar_Cada_Linha_Excel')?['Bucket']}",
  "Timestamp": "@{utcNow()}"
}
```

### ✅ Solução no Modo Código

#### 1. Remover Debug_Verificar_Logica:
Simplesmente delete o bloco inteiro:
```json
// ❌ REMOVER ISTO:
"Debug_Verificar_Logica": {
  "type": "Compose",
  "inputs": { ... },
  "runAfter": { ... }
}
```

E ajuste o `runAfter` da ação seguinte:
```json
"Verificar_Se_Deve_Criar_Tarefa": {
  "type": "If",
  // ANTES:
  // "runAfter": { "Debug_Verificar_Logica": ["Succeeded"] }
  
  // DEPOIS:
  "runAfter": { "Verificar_Tarefa_Existe": ["Succeeded"] }
}
```

#### 2. Adicionar logs específicos:

**Dentro do "If yes" de Verificar_Se_Deve_Criar_Tarefa:**
```json
"actions": {
  "Criar_Nova_Tarefa_Planner": {
    "type": "OpenApiConnection",
    // ... config existente
    "runAfter": {}
  },
  "Log_Tarefa_Criada": {
    "type": "Compose",
    "inputs": {
      "Status": "Criada",
      "Tarefa": "@items('Processar_Cada_Linha_Excel')?['Nome da Tarefa']",
      "Bucket": "@items('Processar_Cada_Linha_Excel')?['Bucket']",
      "Timestamp": "@utcNow()"
    },
    "runAfter": {
      "Criar_Nova_Tarefa_Planner": ["Succeeded"]
    }
  }
}
```

**Dentro do "else" de Verificar_Se_Deve_Criar_Tarefa:**
```json
"else": {
  "actions": {
    "Log_Tarefa_Ignorada": {
      "type": "Compose",
      "inputs": {
        "Status": "Ignorada",
        "Motivo": "@if(greater(length(body('Verificar_Tarefa_Existe')), 0), 'Tarefa já existe', 'Bucket não encontrado')",
        "Tarefa": "@items('Processar_Cada_Linha_Excel')?['Nome da Tarefa']",
        "Bucket": "@items('Processar_Cada_Linha_Excel')?['Bucket']",
        "Timestamp": "@utcNow()"
      },
      "runAfter": {}
    }
  }
}
```

---

## Correção #8: Tratar erro na criação de tarefa

### ❓ Por que fazer?
Se a criação de uma tarefa falhar, as outras tarefas devem continuar sendo processadas (não parar tudo).

### 📍 Onde adicionar?
Após `Criar_Nova_Tarefa_Planner`, em paralelo ao log de sucesso.

### ✅ Solução no Designer (Visual)

#### Passo 1: Adicionar ação paralela
1. Após `Criar_Nova_Tarefa_Planner`, procure o ícone **[+]**
2. Escolha **"Add a parallel branch"**

#### Passo 2: Configurar para executar em erro
1. Na nova ação, adicione **"Compose"**
2. Nomeie: `Tratar_Erro_Criacao`
3. Clique nos **três pontos (...)** desta nova ação
4. Escolha **"Configure run after"**
5. **Desmarque** "is successful"
6. **Marque** "has failed"
7. **Marque** "has timed out"

#### Passo 3: Configurar o conteúdo
**Inputs** do Compose:
```json
{
  "Status": "Erro ao criar",
  "Tarefa": "@{items('Processar_Cada_Linha_Excel')?['Nome da Tarefa']}",
  "Bucket": "@{items('Processar_Cada_Linha_Excel')?['Bucket']}",
  "Erro": "@{body('Criar_Nova_Tarefa_Planner')}",
  "Timestamp": "@{utcNow()}"
}
```

### ✅ Solução no Modo Código

Adicione no mesmo nível que `Log_Tarefa_Criada`:

```json
"actions": {
  "Criar_Nova_Tarefa_Planner": {
    "type": "OpenApiConnection",
    // ... config existente
    "runAfter": {}
  },
  "Log_Tarefa_Criada": {
    "type": "Compose",
    "inputs": {
      "Status": "Criada",
      "Tarefa": "@items('Processar_Cada_Linha_Excel')?['Nome da Tarefa']",
      "Bucket": "@items('Processar_Cada_Linha_Excel')?['Bucket']",
      "Timestamp": "@utcNow()"
    },
    "runAfter": {
      "Criar_Nova_Tarefa_Planner": ["Succeeded"]
    }
  },
  "Tratar_Erro_Criacao": {
    "type": "Compose",
    "inputs": {
      "Status": "Erro ao criar",
      "Tarefa": "@items('Processar_Cada_Linha_Excel')?['Nome da Tarefa']",
      "Bucket": "@items('Processar_Cada_Linha_Excel')?['Bucket']",
      "Erro": "@body('Criar_Nova_Tarefa_Planner')",
      "Timestamp": "@utcNow()"
    },
    "runAfter": {
      "Criar_Nova_Tarefa_Planner": ["Failed", "TimedOut"]
    }
  }
}
```

**Estrutura visual**:
```
Criar_Nova_Tarefa_Planner
       ├─ Succeeded → Log_Tarefa_Criada
       │
       └─ Failed/TimedOut → Tratar_Erro_Criacao
```

---

# 📊 Verificação Final

## Checklist após aplicar correções:

### ✅ Estrutura:
- [ ] ForEach tem nome `Processar_Cada_Linha_Excel`
- [ ] Primeira ação do ForEach tem `runAfter: {}`
- [ ] Ações principais têm tratamento de erro
- [ ] Concorrência está habilitada (20)

### ✅ Validações:
- [ ] Valida se Excel tem dados antes de processar
- [ ] Valida se campos estão vazios/null
- [ ] Verifica bucket existe antes de criar tarefa
- [ ] Verifica tarefa não existe antes de criar

### ✅ Logging:
- [ ] Log quando tarefa é criada
- [ ] Log quando tarefa já existe
- [ ] Log quando bucket não encontrado
- [ ] Log quando dados inválidos
- [ ] Log quando Excel está vazio
- [ ] Log quando ocorrem erros

### ✅ Performance:
- [ ] ForEach processa em paralelo
- [ ] Excel vazio não executa ações desnecessárias

---

# 🧪 Testar o Fluxo

## Teste 1: Fluxo Normal
1. Excel com 3 linhas válidas
2. Buckets existem
3. Tarefas não existem
4. **Esperado**: 3 tarefas criadas, 3 logs de sucesso

## Teste 2: Tarefas Duplicadas
1. Execute o fluxo 2 vezes seguidas
2. **Esperado**: 
   - 1ª execução: tarefas criadas
   - 2ª execução: nenhuma tarefa criada, logs "já existe"

## Teste 3: Bucket Inválido
1. Excel com linha tendo bucket "BucketInexistente"
2. **Esperado**: Log "bucket não encontrado"

## Teste 4: Dados Vazios
1. Excel com linha vazia ou null
2. **Esperado**: Log "dados inválidos"

## Teste 5: Excel Vazio
1. Tabela sem linhas
2. **Esperado**: Log "Excel vazio", fluxo termina rápido

---

# 📞 Solução de Problemas

## Erro: "The template language expression 'items(...)' cannot be evaluated"
**Causa**: ForEach sem nome ou nome incorreto
**Solução**: Aplicar Correção #1

## Erro: "The action requires input 'runAfter'"
**Causa**: Ação sem runAfter definido
**Solução**: Aplicar Correção #2

## Fluxo muito lento
**Causa**: Concorrência desabilitada
**Solução**: Aplicar Correção #5

## Erro 429: Too Many Requests
**Causa**: Concorrência muito alta
**Solução**: Reduzir valor de 20 para 10 ou 5

## Tarefa criada com nome vazio
**Causa**: Validação ausente
**Solução**: Aplicar Correção #4

---

# 💡 Dicas Finais

1. **Sempre teste em ambiente de desenvolvimento primeiro**
2. **Faça backup antes de modificar** (exporte o fluxo)
3. **Aplique correções uma de cada vez** e teste
4. **Monitore logs** nas primeiras execuções
5. **Comece com concorrência baixa** (5) e aumente gradualmente
6. **Documente** quais correções aplicou e quando

---

**Precisa de ajuda?** Entre em contato com o time de automação ou consulte a documentação da Microsoft Power Automate.