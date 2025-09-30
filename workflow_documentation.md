# Power Automate Workflow Documentation

## Overview
This workflow synchronizes tasks from an Excel spreadsheet in SharePoint to Microsoft Planner, creating new tasks only if they don't already exist.

## Trigger Configuration

**Type:** Recurrence  
**Frequency:** Every 1 hour  
**Time Zone:** E. South America Standard Time (Brazil)

## Workflow Steps

### 1. Get Excel Data (`Obter_Dados_Excel`)
- **Action:** Excel Online (Business) - Get Items
- **Source:** SharePoint site `petrobrasbr.sharepoint.com`
- **File Path:** `/1.Gerência/Controles/Planner_Tarefas_Unificadas.xlsx`
- **Table ID:** `{92AC1A55-2203-4675-8AEA-A904F23A71D8}`
- **Expected Columns:**
  - `Nome da Tarefa` (Task Name)
  - `Bucket` (Bucket Name)

### 2. List All Buckets (`Listar_Todos_Buckets`)
- **Action:** Planner - List Buckets
- **Group ID:** `332dd89f-c104-4ae6-96a9-6a45b8ec6f6f`
- **Plan ID:** `XLO7WAvmFEGU07P6t_UH4WQAF9gY`
- **Runs After:** Excel data retrieval succeeds

### 3. Get Existing Tasks (`Obter_Tarefas_Existentes`)
- **Action:** Planner - List Tasks
- **Group ID:** `332dd89f-c104-4ae6-96a9-6a45b8ec6f6f`
- **Plan ID:** `XLO7WAvmFEGU07P6t_UH4WQAF9gY`
- **Runs After:** Bucket listing succeeds

### 4. Process Each Excel Row (`Processar_Cada_Linha_Excel`)
**Type:** For Each Loop  
**Iterates Over:** All rows from Excel data

#### 4.1 Find Matching Bucket (`Encontrar_Bucket_Correspondente`)
- **Action:** Query/Filter
- **Logic:** Finds bucket where `name` equals Excel row's `Bucket` field

#### 4.2 Check if Task Exists (`Verificar_Tarefa_Existe`)
- **Action:** Query/Filter
- **Logic:** Finds task where `title` equals Excel row's `Nome da Tarefa` field
- **Runs After:** Bucket search completes

#### 4.3 Debug Logic (`Debug_Verificar_Logica`)
- **Action:** Compose
- **Purpose:** Creates debug output showing:
  1. Excel row data
  2. Bucket name being searched
  3. Whether bucket was found (count)
  4. Task name being searched
  5. Whether task already exists (count)
  6. Whether task should be created (boolean)

#### 4.4 Decide to Create Task (`Verificar_Se_Deve_Criar_Tarefa`)
- **Action:** Conditional (If)
- **Condition:** 
  - Task does NOT exist (count = 0) AND
  - Bucket was found (count > 0)

##### 4.4.1 If True: Create New Task (`Criar_Nova_Tarefa_Planner`)
- **Action:** Planner - Create Task
- **Parameters:**
  - Group ID: `332dd89f-c104-4ae6-96a9-6a45b8ec6f6f`
  - Plan ID: `XLO7WAvmFEGU07P6t_UH4WQAF9gY`
  - Title: From Excel `Nome da Tarefa`
  - Bucket ID: From matched bucket

##### 4.4.2 If False: Log Skip (`Log_Tarefa_Ja_Existe`)
- **Action:** Compose
- **Output:** "Tarefa já existe ou bucket não encontrado: {task name}"

## Workflow Diagram

```
┌─────────────────────┐
│  Hourly Trigger     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Get Excel Data     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  List All Buckets   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  List All Tasks     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  For Each Excel Row │
│                     │
│  ┌───────────────┐  │
│  │ Find Bucket   │  │
│  └───────┬───────┘  │
│          │          │
│  ┌───────▼───────┐  │
│  │ Check Task    │  │
│  │ Exists        │  │
│  └───────┬───────┘  │
│          │          │
│  ┌───────▼───────┐  │
│  │ Debug Info    │  │
│  └───────┬───────┘  │
│          │          │
│  ┌───────▼───────┐  │
│  │ If Should     │  │
│  │ Create?       │  │
│  │               │  │
│  │ Yes ┌─────┐   │  │
│  │ ────► Create│  │  │
│  │     │ Task │  │  │
│  │     └─────┘   │  │
│  │               │  │
│  │ No  ┌─────┐   │  │
│  │ ────► Log  │  │  │
│  │     │ Skip │  │  │
│  │     └─────┘   │  │
│  └───────────────┘  │
└─────────────────────┘
```

## Key Configuration Values

| Parameter | Value |
|-----------|-------|
| SharePoint Site | `petrobrasbr.sharepoint.com` |
| Site ID | `578615aa-234b-4aec-af9d-0be56c810016` |
| Drive ID | `b!qhWGV0sj7EqvnQvlbIEAFoGthy5Q6M1IpKcSC84Nc6DrX9IW9jMdRJOLnwRSgrL8` |
| File ID | `01467YMNF5OGHA7AWVMRCLBBKQGHYWY7QA` |
| Table ID | `{92AC1A55-2203-4675-8AEA-A904F23A71D8}` |
| Planner Group ID | `332dd89f-c104-4ae6-96a9-6a45b8ec6f6f` |
| Planner Plan ID | `XLO7WAvmFEGU07P6t_UH4WQAF9gY` |

## Business Logic

1. **Idempotency:** Tasks are only created if they don't already exist (checked by title)
2. **Validation:** Tasks are only created if the target bucket exists
3. **Source of Truth:** Excel spreadsheet is the master data source
4. **Frequency:** Sync runs every hour
5. **Conflict Resolution:** Existing tasks are not modified or updated

## Error Handling Considerations

The current workflow should handle:
- ✅ Duplicate task prevention
- ✅ Missing bucket handling
- ⚠️ **Not Handled:** API throttling/rate limits
- ⚠️ **Not Handled:** Excel file access failures
- ⚠️ **Not Handled:** Invalid data in Excel (empty task names, etc.)
- ⚠️ **Not Handled:** Task updates (only creates, never updates)

## Potential Improvements

1. Add error handling and retry logic
2. Send notifications on failures
3. Add support for updating existing tasks
4. Include more task properties (due date, assignments, priority)
5. Add data validation before task creation
6. Implement logging to a tracking table
7. Add support for task deletion when removed from Excel