"""
Python equivalent of the Power Automate workflow for Excel to Planner sync.
This script demonstrates the logic flow and could be adapted for actual use
with appropriate Microsoft Graph API authentication.

Requirements:
- msal (for authentication)
- requests (for API calls)
- python-dotenv (for environment variables)
"""

import os
import time
from typing import List, Dict, Optional
from dataclasses import dataclass
import requests


@dataclass
class WorkflowConfig:
    """Configuration for the workflow"""
    sharepoint_site: str = "petrobrasbr.sharepoint.com"
    site_id: str = "578615aa-234b-4aec-af9d-0be56c810016"
    drive_id: str = "b!qhWGV0sj7EqvnQvlbIEAFoGthy5Q6M1IpKcSC84Nc6DrX9IW9jMdRJOLnwRSgrL8"
    file_id: str = "01467YMNF5OGHA7AWVMRCLBBKQGHYWY7QA"
    table_id: str = "{92AC1A55-2203-4675-8AEA-A904F23A71D8}"
    planner_group_id: str = "332dd89f-c104-4ae6-96a9-6a45b8ec6f6f"
    planner_plan_id: str = "XLO7WAvmFEGU07P6t_UH4WQAF9gY"
    file_path: str = "/1.Gerência/Controles/Planner_Tarefas_Unificadas.xlsx"


class ExcelPlannerSync:
    """Main class for syncing Excel data to Microsoft Planner"""
    
    def __init__(self, config: WorkflowConfig, access_token: str):
        self.config = config
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        self.graph_api_base = "https://graph.microsoft.com/v1.0"
    
    def get_excel_data(self) -> List[Dict]:
        """
        Step 1: Get data from Excel table in SharePoint
        Returns list of rows from the Excel table
        """
        url = (
            f"{self.graph_api_base}/drives/{self.config.drive_id}/"
            f"items/{self.config.file_id}/workbook/tables/{self.config.table_id}/rows"
        )
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            # Parse Excel rows into structured format
            rows = []
            for item in data.get("value", []):
                values = item.get("values", [[]])[0]
                # Assuming columns: [Nome da Tarefa, Bucket, ...]
                if len(values) >= 2:
                    rows.append({
                        "Nome da Tarefa": values[0],
                        "Bucket": values[1]
                    })
            
            print(f"✓ Retrieved {len(rows)} rows from Excel")
            return rows
        
        except requests.exceptions.RequestException as e:
            print(f"✗ Error getting Excel data: {e}")
            return []
    
    def list_all_buckets(self) -> List[Dict]:
        """
        Step 2: Get all buckets from the Planner plan
        """
        url = (
            f"{self.graph_api_base}/planner/plans/{self.config.planner_plan_id}/buckets"
        )
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            buckets = response.json().get("value", [])
            
            print(f"✓ Retrieved {len(buckets)} buckets from Planner")
            return buckets
        
        except requests.exceptions.RequestException as e:
            print(f"✗ Error getting buckets: {e}")
            return []
    
    def list_all_tasks(self) -> List[Dict]:
        """
        Step 3: Get all existing tasks from the Planner plan
        """
        url = (
            f"{self.graph_api_base}/planner/plans/{self.config.planner_plan_id}/tasks"
        )
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            tasks = response.json().get("value", [])
            
            print(f"✓ Retrieved {len(tasks)} tasks from Planner")
            return tasks
        
        except requests.exceptions.RequestException as e:
            print(f"✗ Error getting tasks: {e}")
            return []
    
    def find_bucket_by_name(self, buckets: List[Dict], bucket_name: str) -> Optional[Dict]:
        """
        Find a bucket by its name
        Equivalent to: Encontrar_Bucket_Correspondente
        """
        for bucket in buckets:
            if bucket.get("name") == bucket_name:
                return bucket
        return None
    
    def task_exists(self, tasks: List[Dict], task_title: str) -> bool:
        """
        Check if a task with the given title already exists
        Equivalent to: Verificar_Tarefa_Existe
        """
        for task in tasks:
            if task.get("title") == task_title:
                return True
        return False
    
    def create_task(self, task_title: str, bucket_id: str) -> bool:
        """
        Create a new task in Planner
        Equivalent to: Criar_Nova_Tarefa_Planner
        """
        url = f"{self.graph_api_base}/planner/tasks"
        
        payload = {
            "planId": self.config.planner_plan_id,
            "bucketId": bucket_id,
            "title": task_title
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            print(f"  ✓ Created task: {task_title}")
            return True
        
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Error creating task '{task_title}': {e}")
            return False
    
    def process_excel_row(
        self, 
        row: Dict, 
        buckets: List[Dict], 
        existing_tasks: List[Dict]
    ) -> Dict:
        """
        Process a single Excel row
        Equivalent to: Loop iteration in Processar_Cada_Linha_Excel
        """
        task_name = row.get("Nome da Tarefa", "")
        bucket_name = row.get("Bucket", "")
        
        # Find matching bucket
        bucket = self.find_bucket_by_name(buckets, bucket_name)
        bucket_found = bucket is not None
        
        # Check if task already exists
        task_exists = self.task_exists(existing_tasks, task_name)
        
        # Debug information (equivalent to: Debug_Verificar_Logica)
        debug_info = {
            "1_DADOS_EXCEL": row,
            "2_BUCKET_BUSCADO": bucket_name,
            "3_BUCKET_ENCONTRADO": 1 if bucket_found else 0,
            "4_TAREFA_BUSCADA": task_name,
            "5_TAREFA_JA_EXISTE": 1 if task_exists else 0,
            "6_DEVERIA_CRIAR": bucket_found and not task_exists
        }
        
        print(f"\nProcessing: {task_name}")
        print(f"  Bucket: {bucket_name} {'(found)' if bucket_found else '(not found)'}")
        print(f"  Task exists: {task_exists}")
        print(f"  Should create: {debug_info['6_DEVERIA_CRIAR']}")
        
        # Decide whether to create task (equivalent to: Verificar_Se_Deve_Criar_Tarefa)
        if debug_info["6_DEVERIA_CRIAR"]:
            success = self.create_task(task_name, bucket["id"])
            return {**debug_info, "created": success}
        else:
            reason = "Task already exists" if task_exists else "Bucket not found"
            print(f"  ⊘ Skipped: {reason}")
            return {**debug_info, "created": False, "skip_reason": reason}
    
    def run_sync(self):
        """
        Main workflow execution
        """
        print("=" * 60)
        print("Starting Excel to Planner Sync")
        print("=" * 60)
        
        # Step 1: Get Excel data
        print("\n[1/4] Getting Excel data...")
        excel_rows = self.get_excel_data()
        if not excel_rows:
            print("No data to process. Exiting.")
            return
        
        # Step 2: Get all buckets
        print("\n[2/4] Getting Planner buckets...")
        buckets = self.list_all_buckets()
        
        # Step 3: Get all existing tasks
        print("\n[3/4] Getting existing Planner tasks...")
        existing_tasks = self.list_all_tasks()
        
        # Step 4: Process each Excel row
        print("\n[4/4] Processing Excel rows...")
        print("-" * 60)
        
        results = {
            "total": len(excel_rows),
            "created": 0,
            "skipped_exists": 0,
            "skipped_no_bucket": 0,
            "errors": 0
        }
        
        for row in excel_rows:
            result = self.process_excel_row(row, buckets, existing_tasks)
            
            if result.get("created"):
                results["created"] += 1
            elif result.get("skip_reason") == "Task already exists":
                results["skipped_exists"] += 1
            elif result.get("skip_reason") == "Bucket not found":
                results["skipped_no_bucket"] += 1
            else:
                results["errors"] += 1
        
        # Summary
        print("\n" + "=" * 60)
        print("Sync Complete - Summary")
        print("=" * 60)
        print(f"Total rows processed:    {results['total']}")
        print(f"Tasks created:           {results['created']}")
        print(f"Skipped (already exist): {results['skipped_exists']}")
        print(f"Skipped (no bucket):     {results['skipped_no_bucket']}")
        print(f"Errors:                  {results['errors']}")
        print("=" * 60)


def get_access_token() -> str:
    """
    Get Microsoft Graph API access token
    This is a placeholder - implement actual authentication using MSAL
    """
    # In production, use MSAL (Microsoft Authentication Library)
    # Example:
    # from msal import ConfidentialClientApplication
    # 
    # app = ConfidentialClientApplication(
    #     client_id=os.getenv("CLIENT_ID"),
    #     client_credential=os.getenv("CLIENT_SECRET"),
    #     authority=f"https://login.microsoftonline.com/{os.getenv('TENANT_ID')}"
    # )
    # result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    # return result["access_token"]
    
    return os.getenv("GRAPH_ACCESS_TOKEN", "")


def run_hourly_sync():
    """
    Run the sync process hourly (equivalent to the recurrence trigger)
    """
    config = WorkflowConfig()
    
    print("Starting hourly sync scheduler...")
    print(f"Time Zone: E. South America Standard Time")
    print(f"Frequency: Every 1 hour\n")
    
    while True:
        try:
            access_token = get_access_token()
            if not access_token:
                print("Error: No access token available. Set GRAPH_ACCESS_TOKEN environment variable.")
                break
            
            sync = ExcelPlannerSync(config, access_token)
            sync.run_sync()
            
            print(f"\nNext sync in 1 hour...")
            time.sleep(3600)  # Sleep for 1 hour
            
        except KeyboardInterrupt:
            print("\n\nSync scheduler stopped by user.")
            break
        except Exception as e:
            print(f"\n\nUnexpected error: {e}")
            print("Retrying in 5 minutes...")
            time.sleep(300)


if __name__ == "__main__":
    # For one-time execution (testing)
    config = WorkflowConfig()
    access_token = get_access_token()
    
    if access_token:
        sync = ExcelPlannerSync(config, access_token)
        sync.run_sync()
    else:
        print("Error: No access token available.")
        print("Set the GRAPH_ACCESS_TOKEN environment variable or implement MSAL authentication.")
        print("\nTo run hourly sync, call: run_hourly_sync()")