# Guia Visual com Referências de Interface

## 🖼️ Como Navegar na Interface do Power Automate

### Acessando o Fluxo

```
1. Acesse: https://make.powerautomate.com

2. Menu lateral esquerdo:
   ┌────────────────────┐
   │ 🏠 Home            │
   │ ➕ Create          │
   │ 📋 My flows        │ ← CLIQUE AQUI
   │ 📊 Templates       │
   │ 🔌 Connectors      │
   └────────────────────┘

3. Na lista de fluxos:
   ┌─────────────────────────────────────────────────────┐
   │ 🔍 Search flows...                                  │
   ├─────────────────────────────────────────────────────┤
   │ Name                    Status    Last modified     │
   ├─────────────────────────────────────────────────────┤
   │ Excel to Planner Sync   On       Today             │
   │                         [Edit] [⋮]                 │ ← CLIQUE EM EDIT
   └─────────────────────────────────────────────────────┘
```

---

## 📱 Anatomia da Interface do Editor

```
┌────────────────────────────────────────────────────────────────┐
│ ⬅ Back    Excel to Planner Sync          Save  Test  [⋮] </> │ ← Barra superior
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────────────────────────┐                    │
│  │ 🔁 Recurrence                        │                    │
│  │ Every 1 hour                          │                    │
│  └──────────────────────────────────────┘                    │
│                    ↓                                          │
│  ┌──────────────────────────────────────┐                    │
│  │ 📊 Get items (Obter_Dados_Excel)     │ ← Ação            │
│  │                                   [⋮] │ ← Menu contextual │
│  └──────────────────────────────────────┘                    │
│                    │                                          │
│                   [+] ← Adicionar ação                        │
│                    │                                          │
│  ┌──────────────────────────────────────┐                    │
│  │ 🪣 List buckets                      │                    │
│  └──────────────────────────────────────┘                    │
│                                                                │
└────────────────────────────────────────────────────────────────┘
           ↑                                              ↑
      Canvas                                       Código (</>)
```

### Elementos Importantes:

1. **[⋮]** = Menu de 3 pontos (aparece em cada ação)
   - Rename
   - Settings
   - Delete
   - Configure run after
   - Copy to my clipboard

2. **[+]** = Adicionar nova ação/branch

3. **</>** = Ver código (Peek code)

4. **Save** = Salvar alterações

5. **Test** = Testar o fluxo

---

## 🔧 Correção #1: Renomear ForEach

### Passo Visual:

```
1. Encontre o bloco "Apply to each":

   ┌────────────────────────────────────────┐
   │ Apply to each                    [⋮]   │ ← Clique aqui
   │                                         │
   │ Select an output from previous steps:  │
   │ [💡 value]                              │
   │                                         │
   │ ┌─────────────────────────────────┐   │
   │ │ (ações internas)                 │   │
   │ └─────────────────────────────────┘   │
   └────────────────────────────────────────┘

2. Menu que aparece ao clicar [⋮]:
   ┌──────────────────────┐
   │ Rename               │ ← CLIQUE AQUI
   │ Settings             │
   │ Delete               │
   │ Copy to my clipboard │
   └──────────────────────┘

3. Janela de renomear:
   ┌─────────────────────────────────────┐
   │ Rename Apply to each                │
   ├─────────────────────────────────────┤
   │ Name:                               │
   │ ┌─────────────────────────────────┐ │
   │ │ Processar_Cada_Linha_Excel      │ │ ← Digite exatamente isso
   │ └─────────────────────────────────┘ │
   │                                     │
   │              [Cancel]  [Rename]     │ ← Clique Rename
   └─────────────────────────────────────┘
```

---

## 🔧 Correção #3: Adicionar Tratamento de Erro

### Visualização do "Configure Run After":

```
1. Adicione uma ação após "Obter_Dados_Excel"

2. Na NOVA ação, clique [⋮] → Configure run after:

   ┌──────────────────────────────────────────┐
   │ Configure run after                      │
   ├──────────────────────────────────────────┤
   │ Obter_Dados_Excel                        │
   │                                          │
   │ Select the status:                       │
   │ ☐ is successful                          │ ← DESMARQUE
   │ ☑ has failed                             │ ← MARQUE
   │ ☐ is skipped                             │
   │ ☑ has timed out                          │ ← MARQUE
   │                                          │
   │                        [Cancel]  [Done]  │
   └──────────────────────────────────────────┘

3. Resultado visual no canvas:

   ┌────────────────────────────┐
   │ Obter_Dados_Excel          │
   └──────┬─────────────────────┘
          │
          ├─────────► (succeeded) ─► Listar_Todos_Buckets
          │
          └─────────► (failed/timeout) ─► Tratar_Erro_Excel
```

---

## 🔧 Correção #4: Adicionar Validação (Condition)

### Como Adicionar Condition:

```
1. Dentro do ForEach, clique [+] New step

2. Busque "Condition":
   ┌─────────────────────────────────────┐
   │ 🔍 Search connectors and actions    │
   │ condition                           │
   ├─────────────────────────────────────┤
   │ Actions                             │
   │ ┌─────────────────────────────────┐ │
   │ │ ⚖️  Condition                    │ │ ← SELECIONE
   │ │     Control                      │ │
   │ └─────────────────────────────────┘ │
   └─────────────────────────────────────┘

3. Configurar a Condition (modo básico):
   ┌──────────────────────────────────────────────────┐
   │ Condition                                        │
   ├──────────────────────────────────────────────────┤
   │ ┌──────────┐  ┌──────────────┐  ┌────────────┐ │
   │ │ Nome da  │  │ is not equal │  │            │ │
   │ │ Tarefa   │  │ to           │  │            │ │
   │ └──────────┘  └──────────────┘  └────────────┘ │
   │                                                  │
   │ [+ Add] ← Adicionar outra condição (AND/OR)     │
   │                                                  │
   │ [Edit in advanced mode]  ← CLIQUE AQUI (melhor) │
   └──────────────────────────────────────────────────┘

4. Modo avançado:
   ┌──────────────────────────────────────────────────┐
   │ Condition                                        │
   ├──────────────────────────────────────────────────┤
   │ [fx] Edit in advanced mode                       │
   │                                                  │
   │ ┌──────────────────────────────────────────────┐ │
   │ │ and(                                         │ │
   │ │   not(equals(                                │ │
   │ │     coalesce(                                │ │ ← COLE A EXPRESSÃO AQUI
   │ │       items('...')?['Nome da Tarefa'],       │ │
   │ │       ''), '')),                             │ │
   │ │   not(equals(...))                           │ │
   │ │ )                                            │ │
   │ └──────────────────────────────────────────────┘ │
   └──────────────────────────────────────────────────┘

5. Resultado - Estrutura If/Else:
   ┌──────────────────────────────────────────────────┐
   │ Condition                                        │
   ├──────────────────────────────────────────────────┤
   │ ┌────────────────┐      ┌────────────────┐      │
   │ │ If yes         │      │ If no          │      │
   │ │                │      │                │      │
   │ │ [+ Add action] │      │ [+ Add action] │      │
   │ │                │      │                │      │
   │ └────────────────┘      └────────────────┘      │
   └──────────────────────────────────────────────────┘
```

---

## 🔧 Correção #5: Habilitar Concorrência

### Interface de Configuração:

```
1. No ForEach, clique [⋮] → Settings:

   ┌─────────────────────────────────────────────┐
   │ Settings for Processar_Cada_Linha_Excel     │
   ├─────────────────────────────────────────────┤
   │                                             │
   │ Concurrency Control                         │
   │ Run actions in parallel to speed up the    │
   │ execution of the loop iterations            │
   │                                             │
   │ ◉ Off    ○ On                               │ ← Mude para ON
   │                                             │
   └─────────────────────────────────────────────┘

2. Após ativar (On):

   ┌─────────────────────────────────────────────┐
   │ Settings for Processar_Cada_Linha_Excel     │
   ├─────────────────────────────────────────────┤
   │                                             │
   │ Concurrency Control                         │
   │ ○ Off    ◉ On                               │
   │                                             │
   │ Degree of Parallelism                       │
   │ How many instances of this loop should run  │
   │ at the same time (1-50)                     │
   │                                             │
   │ 1  [────●──────────────────────────]  50    │ ← Arraste para 20
   │         20                                  │
   │                                             │
   │ ℹ️ Tip: Start with a low number and test   │
   │                                             │
   │                        [Cancel]  [Done]     │
   └─────────────────────────────────────────────┘
```

---

## 🔍 Como Usar Dynamic Content e Expressions

### Dynamic Content:

```
1. Ao clicar em um campo de input, painel aparece à direita:

   ┌─────────────────────────────────────┐
   │ 🔍 Search                           │
   │ ┌─────────────────────────────────┐ │
   │ │                                 │ │
   │ └─────────────────────────────────┘ │
   │                                     │
   │ Tabs:                               │
   │ [Dynamic content] [Expression]      │ ← Duas abas
   │                                     │
   │ Obter_Dados_Excel                   │
   │ └─ value                            │ ← Clique para inserir
   │                                     │
   │ Current item (Apply to each)        │
   │ └─ Nome da Tarefa                   │
   │ └─ Bucket                           │
   │                                     │
   └─────────────────────────────────────┘
```

### Expression:

```
1. Clique na aba [Expression]:

   ┌─────────────────────────────────────┐
   │ 🔍 Search                           │
   │ ┌─────────────────────────────────┐ │
   │ │ length(                         │ │ ← Digite aqui
   │ └─────────────────────────────────┘ │
   │                                     │
   │ [Dynamic content] [Expression]      │
   │                                     │
   │ String functions                    │
   │ └─ concat                           │
   │ └─ substring                        │
   │ └─ length                           │ ← Ou clique para inserir
   │                                     │
   │ Logical comparison functions        │
   │ └─ equals                           │
   │ └─ greater                          │
   │ └─ and                              │
   │ └─ or                               │
   │ └─ not                              │
   │                                     │
   │                      [OK] [Cancel]  │
   └─────────────────────────────────────┘

2. Para combinar expression com dynamic content:
   - Digite: length(body('Obter_Dados_Excel')
   - Clique na aba [Dynamic content]
   - Clique em "value"
   - Complete: )
   - Resultado: length(body('Obter_Dados_Excel')?['value'])
```

---

## 📊 Visualização do Fluxo Completo Corrigido

```
┌────────────────────────────────────────────────────────────┐
│ 🔁 Recurrence                                              │
│    Every 1 hour                                            │
└──────────────────────┬─────────────────────────────────────┘
                       ↓
┌────────────────────────────────────────────────────────────┐
│ 📊 Obter_Dados_Excel                                       │
└──────────────────────┬─────────────────────────────────────┘
                       │
                       ├──► (succeeded) ──┐
                       │                  ↓
                       │         ┌────────────────────────────┐
                       │         │ Verificar_Excel_Com_Dados  │
                       │         │ (Condition)                │
                       │         ├────────────┬───────────────┤
                       │         │ If yes     │ If no         │
                       │         │            │               │
                       │         │ ┌────────┐ │ ┌───────────┐│
                       │         │ │Listar  │ │ │Log Excel  ││
                       │         │ │Buckets │ │ │Vazio      ││
                       │         │ └───┬────┘ │ └───────────┘│
                       │         │     ↓      │               │
                       │         │ ┌────────┐ │               │
                       │         │ │Obter   │ │               │
                       │         │ │Tarefas │ │               │
                       │         │ └───┬────┘ │               │
                       │         │     ↓      │               │
                       │         │ ┌────────┐ │               │
                       │         │ │ForEach │ │               │
                       │         │ │(x20)   │ │               │
                       │         │ │        │ │               │
                       │         │ │┌──────┐│ │               │
                       │         │ ││Valid.││ │               │
                       │         │ ││Dados ││ │               │
                       │         │ │└──┬───┘│ │               │
                       │         │ │   ↓    │ │               │
                       │         │ │[If/Else│ │               │
                       │         │ │]       │ │               │
                       │         │ └────────┘ │               │
                       │         └────────────┴───────────────┘
                       │
                       └──► (failed/timeout) ──┐
                                                ↓
                                       ┌────────────────┐
                                       │Tratar_Erro     │
                                       │Excel           │
                                       └────────────────┘

Legenda:
🔁 = Trigger (gatilho)
📊 = Ação de dados
⚖️  = Condition (If/Else)
🔄 = ForEach
📝 = Compose (log)
```

---

## 🎨 Cores e Ícones no Power Automate

As ações têm cores diferentes para facilitar identificação:

```
🔵 Azul = Ações de controle (Condition, ForEach, etc.)
🟢 Verde = Ações bem-sucedidas (após execução)
🔴 Vermelho = Ações com erro (após execução)
🟡 Amarelo = Ações puladas/skipped (após execução)
⚪ Cinza = Ações não executadas ainda

Conectores comuns:
📊 Excel Online = Verde escuro
📋 Planner = Roxo
📧 Outlook = Azul
🗂️  SharePoint = Azul
```

---

## 📱 Testando o Fluxo

### Interface de Teste:

```
1. Clique no botão [Test] no canto superior direito:

   ┌────────────────────────────────────┐
   │ Test Flow                          │
   ├────────────────────────────────────┤
   │                                    │
   │ ◉ Manually                         │ ← Selecione
   │   I'll perform the trigger action. │
   │                                    │
   │ ○ Automatically                    │
   │   With data from a previous run    │
   │                                    │
   │                    [Test] [Cancel] │
   └────────────────────────────────────┘

2. Após clicar Test, o fluxo inicia:

   ┌────────────────────────────────────────┐
   │ ⏸️  Running                            │
   │ Your flow is running. You can leave   │
   │ this page and come back later.        │
   └────────────────────────────────────────┘

3. Acompanhar execução:

   Cada ação mostra:
   ┌────────────────────────────────────┐
   │ ✅ Obter_Dados_Excel               │
   │    Duration: 2.3s                  │
   │    [⏷] Show details                │ ← Clique para ver dados
   └────────────────────────────────────┘

   ┌────────────────────────────────────┐
   │ ❌ Criar_Nova_Tarefa_Planner       │
   │    Status: 400 Bad Request         │
   │    [⏷] Show details                │ ← Ver erro
   └────────────────────────────────────┘
```

---

## 💾 Salvando e Exportando

### Salvar:

```
Clique [Save] no topo → Aguarde confirmação:

┌────────────────────────────────┐
│ ✅ Your flow has been saved    │
└────────────────────────────────┘
```

### Exportar (Backup):

```
1. Volte para a lista de fluxos (botão Back)

2. Na lista, clique [⋮] ao lado do fluxo:
   ┌──────────────────────────┐
   │ Edit                     │
   │ Details                  │
   │ Analytics                │
   │ Export                   │ ← CLIQUE AQUI
   │ └─ Package (.zip)        │ ← Selecione
   │ Send a copy              │
   │ Turn off                 │
   │ Delete                   │
   └──────────────────────────┘

3. Configurar exportação:
   ┌────────────────────────────────────┐
   │ Export package                     │
   ├────────────────────────────────────┤
   │ Package name:                      │
   │ ┌────────────────────────────────┐ │
   │ │ Excel-Planner-Sync-Backup      │ │
   │ └────────────────────────────────┘ │
   │                                    │
   │ Description: (opcional)            │
   │                                    │
   │                         [Export]   │
   └────────────────────────────────────┘

4. Download automático do arquivo .zip
```

---

## 🔍 Monitorando Execuções

### Ver histórico:

```
1. Na lista de fluxos, clique no NOME do fluxo (não Edit):

   ┌─────────────────────────────────────────────┐
   │ Excel to Planner Sync                       │
   ├─────────────────────────────────────────────┤
   │ [Overview] [Run history] [Analytics] [Edit] │ ← Clique Run history
   └─────────────────────────────────────────────┘

2. Histórico de execuções:
   ┌─────────────────────────────────────────────────────────┐
   │ Run history                                             │
   ├────────────────┬─────────────┬──────────┬──────────────┤
   │ Start time     │ Duration    │ Status   │              │
   ├────────────────┼─────────────┼──────────┼──────────────┤
   │ 10:00 AM       │ 15s         │ ✅ Success│ [View]       │ ← Clique
   │ 09:00 AM       │ 12s         │ ✅ Success│ [View]       │
   │ 08:00 AM       │ Error       │ ❌ Failed │ [View]       │
   └────────────────┴─────────────┴──────────┴──────────────┘

3. Detalhes da execução:
   - Mostra cada ação executada
   - Inputs e outputs de cada ação
   - Tempo de execução
   - Mensagens de erro (se houver)
```

---

## ⌨️ Atalhos Úteis

```
Ctrl + S     = Salvar
Ctrl + Z     = Desfazer
Ctrl + Y     = Refazer
Ctrl + C     = Copiar ação
Ctrl + V     = Colar ação
Delete       = Deletar ação selecionada
F2           = Renomear ação selecionada (em alguns navegadores)
```

---

## 📞 Onde Encontrar Ajuda

### Documentação Oficial:
- https://learn.microsoft.com/power-automate/

### Comunidade:
- https://powerusers.microsoft.com/

### Suporte Microsoft:
- Portal: https://admin.powerplatform.microsoft.com/support

---

**Dica**: Tire screenshots do seu fluxo ANTES de fazer mudanças grandes, assim você pode comparar depois!