# Exemplos de Código Completo - Antes e Depois

## 📋 Índice
- [ForEach - Antes e Depois](#foreach---antes-e-depois)
- [Tratamento de Erro - Exemplo Completo](#tratamento-de-erro---exemplo-completo)
- [Validação de Dados - Exemplo Completo](#validação-de-dados---exemplo-completo)
- [Fluxo Completo Original](#fluxo-completo-original)
- [Fluxo Completo Corrigido](#fluxo-completo-corrigido)

---

## ForEach - Antes e Depois

### ❌ ANTES (Com Problemas):

```json
{
  "type": "Foreach",
  "foreach": "@body('Obter_Dados_Excel')?['value']",
  "actions": {
    "Encontrar_Bucket_Correspondente": {
      "type": "Query",
      "inputs": {
        "from": "@body('Listar_Todos_Buckets')?['value']",
        "where": "@equals(item()?['name'],items('Processar_Cada_Linha_Excel')?['Bucket'])"
      }
      // ❌ PROBLEMA 1: Falta "runAfter": {}
    },
    "Verificar_Tarefa_Existe": {
      "type": "Query",
      "inputs": {
        "from": "@body('Obter_Tarefas_Existentes')?['value']",
        "where": "@equals(item()?['title'],items('Processar_Cada_Linha_Excel')?['Nome da Tarefa'])"
      },
      "runAfter": {
        "Encontrar_Bucket_Correspondente": ["Succeeded"]
      }
    }
    // ... outras ações
  },
  "runAfter": {
    "Obter_Tarefas_Existentes": ["Succeeded"]
  }
  // ❌ PROBLEMA 2: Falta nome explícito (Processar_Cada_Linha_Excel)
  // ❌ PROBLEMA 3: Sem concorrência
}
```

### ✅ DEPOIS (Corrigido):

```json
"Processar_Cada_Linha_Excel": {
  // ✅ CORREÇÃO 1: Nome explícito como chave do objeto
  "type": "Foreach",
  "foreach": "@body('Obter_Dados_Excel')?['value']",
  "runtimeConfiguration": {
    // ✅ CORREÇÃO 3: Concorrência habilitada
    "concurrency": {
      "repetitions": 20
    }
  },
  "actions": {
    "Encontrar_Bucket_Correspondente": {
      "type": "Query",
      "inputs": {
        "from": "@body('Listar_Todos_Buckets')?['value']",
        "where": "@equals(item()?['name'], items('Processar_Cada_Linha_Excel')?['Bucket'])"
      },
      "runAfter": {}
      // ✅ CORREÇÃO 2: runAfter vazio adicionado
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
    }
    // ... outras ações
  },
  "runAfter": {
    "Obter_Tarefas_Existentes": ["Succeeded"]
  }
}
```

---

## Tratamento de Erro - Exemplo Completo

### Estrutura de Ações com Tratamento de Erro:

```json
{
  "actions": {
    "Obter_Dados_Excel": {
      "type": "OpenApiConnection",
      "inputs": {
        "parameters": {
          "source": "sites/petrobrasbr.sharepoint.com,578615aa-234b-4aec-af9d-0be56c810016,2e87ad81-e850-48cd-a4a7-120bce0d73a0",
          "drive": "b!qhWGV0sj7EqvnQvlbIEAFoGthy5Q6M1IpKcSC84Nc6DrX9IW9jMdRJOLnwRSgrL8",
          "file": "01467YMNF5OGHA7AWVMRCLBBKQGHYWY7QA",
          "table": "{92AC1A55-2203-4675-8AEA-A904F23A71D8}"
        },
        "host": {
          "apiId": "/providers/Microsoft.PowerApps/apis/shared_excelonlinebusiness",
          "connection": "shared_excelonlinebusiness",
          "operationId": "GetItems"
        }
      },
      "runAfter": {},
      "metadata": {
        "01467YMNF5OGHA7AWVMRCLBBKQGHYWY7QA": "/1.Gerência/Controles/Planner_Tarefas_Unificadas.xlsx",
        "tableId": "{92AC1A55-2203-4675-8AEA-A904F23A71D8}"
      }
    },

    // ✅ RAMIFICAÇÃO DE SUCESSO
    "Verificar_Excel_Com_Dados": {
      "type": "If",
      "expression": {
        "greater": [
          "@length(body('Obter_Dados_Excel')?['value'])",
          0
        ]
      },
      "actions": {
        // ... ações normais do fluxo
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
        // ✅ Executa somente se Excel foi obtido com sucesso
      }
    },

    // ✅ RAMIFICAÇÃO DE ERRO (PARALELA)
    "Tratar_Erro_Excel": {
      "type": "Compose",
      "inputs": {
        "Status": "Erro crítico",
        "Motivo": "Falha ao obter dados do Excel",
        "Erro": "@body('Obter_Dados_Excel')",
        "Timestamp": "@utcNow()",
        "Detalhes_Adicionais": {
          "ActionName": "Obter_Dados_Excel",
          "FlowRunId": "@workflow()?['run']?['name']"
        }
      },
      "runAfter": {
        "Obter_Dados_Excel": ["Failed", "TimedOut"]
        // ✅ Executa somente se Excel falhou ou timeout
      }
    },

    // 🔔 OPCIONAL: Enviar notificação por email
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
          "emailMessage/Subject": "❌ Erro no Fluxo Excel → Planner",
          "emailMessage/Body": "<h2>Falha ao obter dados do Excel</h2><p><strong>Horário:</strong> @{utcNow()}</p><p><strong>Ação:</strong> Obter_Dados_Excel</p><p><strong>Flow Run ID:</strong> @{workflow()?['run']?['name']}</p><p>Por favor, verifique o arquivo Excel e as permissões.</p>",
          "emailMessage/Importance": "High"
        }
      },
      "runAfter": {
        "Tratar_Erro_Excel": ["Succeeded"]
        // ✅ Envia email após logar o erro
      }
    }
  }
}
```

### Visualização da Estrutura:

```
Obter_Dados_Excel
       │
       ├─ [Succeeded] ──────► Verificar_Excel_Com_Dados
       │                             │
       │                             ├─ If yes → (continua fluxo)
       │                             └─ If no  → Log_Excel_Vazio
       │
       └─ [Failed/TimedOut] ─► Tratar_Erro_Excel
                                      ↓
                               Enviar_Email_Erro_Excel
```

---

## Validação de Dados - Exemplo Completo

### ForEach com Validação Integrada:

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
    
    // ✅ PRIMEIRA AÇÃO: VALIDAÇÃO
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
      
      // ✅ IF YES: DADOS VÁLIDOS - PROCESSA NORMALMENTE
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
        
        "Verificar_Se_Deve_Criar_Tarefa": {
          "type": "If",
          "expression": {
            "and": [
              {
                "equals": [
                  "@length(body('Verificar_Tarefa_Existe'))",
                  0
                ]
              },
              {
                "greater": [
                  "@length(body('Encontrar_Bucket_Correspondente'))",
                  0
                ]
              }
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
                },
                "host": {
                  "apiId": "/providers/Microsoft.PowerApps/apis/shared_planner",
                  "connection": "shared_planner",
                  "operationId": "CreateTask_V3"
                }
              },
              "runAfter": {}
            },
            
            // ✅ LOG DE SUCESSO
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
            
            // ✅ TRATAMENTO DE ERRO NA CRIAÇÃO
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
          },
          
          "else": {
            "actions": {
              // ✅ LOG DE TAREFA IGNORADA
              "Log_Tarefa_Ignorada": {
                "type": "Compose",
                "inputs": {
                  "Status": "Ignorada",
                  "Motivo": "@if(greater(length(body('Verificar_Tarefa_Existe')), 0), 'Tarefa já existe', 'Bucket não encontrado')",
                  "Tarefa": "@items('Processar_Cada_Linha_Excel')?['Nome da Tarefa']",
                  "Bucket_Buscado": "@items('Processar_Cada_Linha_Excel')?['Bucket']",
                  "Timestamp": "@utcNow()"
                },
                "runAfter": {}
              }
            }
          },
          
          "runAfter": {
            "Verificar_Tarefa_Existe": ["Succeeded"]
          }
        }
      },
      
      // ✅ IF NO: DADOS INVÁLIDOS - LOGA E PULA
      "else": {
        "actions": {
          "Log_Dados_Invalidos": {
            "type": "Compose",
            "inputs": {
              "Status": "Dados inválidos",
              "Motivo": "Nome da tarefa ou bucket vazio/null",
              "Linha_Completa": "@items('Processar_Cada_Linha_Excel')",
              "Nome_Tarefa_Recebido": "@coalesce(items('Processar_Cada_Linha_Excel')?['Nome da Tarefa'], 'NULL')",
              "Bucket_Recebido": "@coalesce(items('Processar_Cada_Linha_Excel')?['Bucket'], 'NULL')",
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

## Fluxo Completo Original

### (Com os problemas identificados)

```json
{
  "definition": {
    "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {},
    "triggers": {
      "Recurrence": {
        "type": "Recurrence",
        "recurrence": {
          "interval": 1,
          "frequency": "Hour",
          "timeZone": "E. South America Standard Time"
        }
      }
    },
    "actions": {
      "Obter_Dados_Excel": {
        "type": "OpenApiConnection",
        "inputs": {
          "parameters": {
            "source": "sites/petrobrasbr.sharepoint.com,578615aa-234b-4aec-af9d-0be56c810016,2e87ad81-e850-48cd-a4a7-120bce0d73a0",
            "drive": "b!qhWGV0sj7EqvnQvlbIEAFoGthy5Q6M1IpKcSC84Nc6DrX9IW9jMdRJOLnwRSgrL8",
            "file": "01467YMNF5OGHA7AWVMRCLBBKQGHYWY7QA",
            "table": "{92AC1A55-2203-4675-8AEA-A904F23A71D8}"
          },
          "host": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_excelonlinebusiness",
            "connection": "shared_excelonlinebusiness",
            "operationId": "GetItems"
          }
        },
        "runAfter": {},
        "metadata": {
          "01467YMNF5OGHA7AWVMRCLBBKQGHYWY7QA": "/1.Gerência/Controles/Planner_Tarefas_Unificadas.xlsx",
          "tableId": "{92AC1A55-2203-4675-8AEA-A904F23A71D8}"
        }
      },
      "Listar_Todos_Buckets": {
        "type": "OpenApiConnection",
        "inputs": {
          "parameters": {
            "groupId": "332dd89f-c104-4ae6-96a9-6a45b8ec6f6f",
            "id": "XLO7WAvmFEGU07P6t_UH4WQAF9gY"
          },
          "host": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_planner",
            "connection": "shared_planner",
            "operationId": "ListBuckets_V3"
          }
        },
        "runAfter": {
          "Obter_Dados_Excel": ["Succeeded"]
        }
      },
      "Obter_Tarefas_Existentes": {
        "type": "OpenApiConnection",
        "inputs": {
          "parameters": {
            "groupId": "332dd89f-c104-4ae6-96a9-6a45b8ec6f6f",
            "id": "XLO7WAvmFEGU07P6t_UH4WQAF9gY"
          },
          "host": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_planner",
            "connection": "shared_planner",
            "operationId": "ListTasks_V3"
          }
        },
        "runAfter": {
          "Listar_Todos_Buckets": ["Succeeded"]
        }
      },
      
      // ❌ PROBLEMA: ForEach sem nome explícito
      "Apply_to_each": {
        "type": "Foreach",
        "foreach": "@body('Obter_Dados_Excel')?['value']",
        "actions": {
          "Encontrar_Bucket_Correspondente": {
            "type": "Query",
            "inputs": {
              "from": "@body('Listar_Todos_Buckets')?['value']",
              "where": "@equals(item()?['name'],items('Processar_Cada_Linha_Excel')?['Bucket'])"
            }
            // ❌ PROBLEMA: Falta runAfter vazio
          },
          "Verificar_Tarefa_Existe": {
            "type": "Query",
            "inputs": {
              "from": "@body('Obter_Tarefas_Existentes')?['value']",
              "where": "@equals(item()?['title'],items('Processar_Cada_Linha_Excel')?['Nome da Tarefa'])"
            },
            "runAfter": {
              "Encontrar_Bucket_Correspondente": ["Succeeded"]
            }
          },
          "Debug_Verificar_Logica": {
            "type": "Compose",
            "inputs": {
              "1_DADOS_EXCEL": "@items('Processar_Cada_Linha_Excel')",
              "2_BUCKET_BUSCADO": "@items('Processar_Cada_Linha_Excel')?['Bucket']",
              "3_BUCKET_ENCONTRADO": "@length(body('Encontrar_Bucket_Correspondente'))",
              "4_TAREFA_BUSCADA": "@items('Processar_Cada_Linha_Excel')?['Nome da Tarefa']",
              "5_TAREFA_JA_EXISTE": "@length(body('Verificar_Tarefa_Existe'))",
              "6_DEVERIA_CRIAR": "@and(equals(length(body('Verificar_Tarefa_Existe')), 0), greater(length(body('Encontrar_Bucket_Correspondente')), 0))"
            },
            "runAfter": {
              "Verificar_Tarefa_Existe": ["Succeeded"]
            }
          },
          "Verificar_Se_Deve_Criar_Tarefa": {
            "type": "If",
            "expression": {
              "and": [
                {
                  "equals": [
                    "@length(body('Verificar_Tarefa_Existe'))",
                    0
                  ]
                },
                {
                  "greater": [
                    "@length(body('Encontrar_Bucket_Correspondente'))",
                    0
                  ]
                }
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
                  },
                  "host": {
                    "apiId": "/providers/Microsoft.PowerApps/apis/shared_planner",
                    "connection": "shared_planner",
                    "operationId": "CreateTask_V3"
                  }
                }
              }
            },
            "else": {
              "actions": {
                "Log_Tarefa_Ja_Existe": {
                  "type": "Compose",
                  "inputs": "Tarefa já existe ou bucket não encontrado: @{items('Processar_Cada_Linha_Excel')?['Nome da Tarefa']}"
                }
              }
            },
            "runAfter": {
              "Debug_Verificar_Logica": ["Succeeded"]
            }
          }
        },
        "runAfter": {
          "Obter_Tarefas_Existentes": ["Succeeded"]
        }
        // ❌ PROBLEMA: Sem concorrência configurada
        // ❌ PROBLEMA: Sem validação de dados vazios
        // ❌ PROBLEMA: Sem tratamento de erro
      }
    }
    // ❌ PROBLEMA: Sem tratamento de erro global
    // ❌ PROBLEMA: Sem verificação de Excel vazio
  }
}
```

---

## Fluxo Completo Corrigido

### (Todas as correções aplicadas)

```json
{
  "definition": {
    "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {},
    "triggers": {
      "Recurrence": {
        "type": "Recurrence",
        "recurrence": {
          "interval": 1,
          "frequency": "Hour",
          "timeZone": "E. South America Standard Time"
        }
      }
    },
    "actions": {
      
      "Obter_Dados_Excel": {
        "type": "OpenApiConnection",
        "inputs": {
          "parameters": {
            "source": "sites/petrobrasbr.sharepoint.com,578615aa-234b-4aec-af9d-0be56c810016,2e87ad81-e850-48cd-a4a7-120bce0d73a0",
            "drive": "b!qhWGV0sj7EqvnQvlbIEAFoGthy5Q6M1IpKcSC84Nc6DrX9IW9jMdRJOLnwRSgrL8",
            "file": "01467YMNF5OGHA7AWVMRCLBBKQGHYWY7QA",
            "table": "{92AC1A55-2203-4675-8AEA-A904F23A71D8}"
          },
          "host": {
            "apiId": "/providers/Microsoft.PowerApps/apis/shared_excelonlinebusiness",
            "connection": "shared_excelonlinebusiness",
            "operationId": "GetItems"
          }
        },
        "runAfter": {},
        "metadata": {
          "01467YMNF5OGHA7AWVMRCLBBKQGHYWY7QA": "/1.Gerência/Controles/Planner_Tarefas_Unificadas.xlsx",
          "tableId": "{92AC1A55-2203-4675-8AEA-A904F23A71D8}"
        }
      },
      
      // ✅ CORREÇÃO #3: Tratamento de erro
      "Tratar_Erro_Excel": {
        "type": "Compose",
        "inputs": {
          "Status": "Erro crítico",
          "Motivo": "Falha ao obter dados do Excel",
          "Erro": "@body('Obter_Dados_Excel')",
          "Timestamp": "@utcNow()"
        },
        "runAfter": {
          "Obter_Dados_Excel": ["Failed", "TimedOut"]
        }
      },
      
      // ✅ CORREÇÃO #6: Verificar Excel vazio
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
            "type": "OpenApiConnection",
            "inputs": {
              "parameters": {
                "groupId": "332dd89f-c104-4ae6-96a9-6a45b8ec6f6f",
                "id": "XLO7WAvmFEGU07P6t_UH4WQAF9gY"
              },
              "host": {
                "apiId": "/providers/Microsoft.PowerApps/apis/shared_planner",
                "connection": "shared_planner",
                "operationId": "ListBuckets_V3"
              }
            },
            "runAfter": {}
          },
          
          "Obter_Tarefas_Existentes": {
            "type": "OpenApiConnection",
            "inputs": {
              "parameters": {
                "groupId": "332dd89f-c104-4ae6-96a9-6a45b8ec6f6f",
                "id": "XLO7WAvmFEGU07P6t_UH4WQAF9gY"
              },
              "host": {
                "apiId": "/providers/Microsoft.PowerApps/apis/shared_planner",
                "connection": "shared_planner",
                "operationId": "ListTasks_V3"
              }
            },
            "runAfter": {
              "Listar_Todos_Buckets": ["Succeeded"]
            }
          },
          
          // ✅ CORREÇÃO #1: ForEach nomeado corretamente
          "Processar_Cada_Linha_Excel": {
            "type": "Foreach",
            "foreach": "@body('Obter_Dados_Excel')?['value']",
            
            // ✅ CORREÇÃO #5: Concorrência habilitada
            "runtimeConfiguration": {
              "concurrency": {
                "repetitions": 20
              }
            },
            
            "actions": {
              
              // ✅ CORREÇÃO #4: Validação de dados
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
                    // ✅ CORREÇÃO #2: runAfter vazio adicionado
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
                  
                  "Verificar_Se_Deve_Criar_Tarefa": {
                    "type": "If",
                    "expression": {
                      "and": [
                        {
                          "equals": [
                            "@length(body('Verificar_Tarefa_Existe'))",
                            0
                          ]
                        },
                        {
                          "greater": [
                            "@length(body('Encontrar_Bucket_Correspondente'))",
                            0
                          ]
                        }
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
                          },
                          "host": {
                            "apiId": "/providers/Microsoft.PowerApps/apis/shared_planner",
                            "connection": "shared_planner",
                            "operationId": "CreateTask_V3"
                          }
                        },
                        "runAfter": {}
                      },
                      
                      // ✅ CORREÇÃO #7: Log estruturado de sucesso
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
                      
                      // ✅ CORREÇÃO #8: Tratamento de erro na criação
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
                    },
                    "else": {
                      "actions": {
                        
                        // ✅ CORREÇÃO #7: Log estruturado de tarefa ignorada
                        "Log_Tarefa_Ignorada": {
                          "type": "Compose",
                          "inputs": {
                            "Status": "Ignorada",
                            "Motivo": "@if(greater(length(body('Verificar_Tarefa_Existe')), 0), 'Tarefa já existe', 'Bucket não encontrado')",
                            "Tarefa": "@items('Processar_Cada_Linha_Excel')?['Nome da Tarefa']",
                            "Bucket_Buscado": "@items('Processar_Cada_Linha_Excel')?['Bucket']",
                            "Timestamp": "@utcNow()"
                          },
                          "runAfter": {}
                        }
                      }
                    },
                    "runAfter": {
                      "Verificar_Tarefa_Existe": ["Succeeded"]
                    }
                  }
                },
                "else": {
                  "actions": {
                    
                    // ✅ CORREÇÃO #4: Log de dados inválidos
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
        },
        "else": {
          "actions": {
            
            // ✅ CORREÇÃO #6: Log de Excel vazio
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
    }
  }
}
```

---

## 📊 Resumo das Diferenças

| Aspecto | Original | Corrigido |
|---------|----------|-----------|
| **Linhas de código** | ~80 | ~250 |
| **Ações totais** | 7 | 15 |
| **Conditions** | 1 | 3 |
| **Logs estruturados** | 1 | 6 |
| **Tratamento de erro** | 0 | 3 pontos |
| **Validações** | 1 | 3 |
| **Concorrência** | Sequencial | Paralelo (20x) |
| **Robustez** | Baixa | Alta |

---

## 🎯 Como Usar Estes Exemplos

1. **Copiar o código corrigido completo** e importar no Power Automate
2. **Ou copiar seções específicas** para aplicar correções pontuais
3. **Ajustar IDs e configurações** conforme seu ambiente
4. **Testar em ambiente de desenvolvimento** antes de produção

---

**💡 Dica**: Use um comparador de JSON online (como jsondiff.com) para ver exatamente o que mudou entre as versões!