"""
BigQuery Client for Colombia Economic Insights
Connects to Google Cloud BigQuery to fetch economic data
"""

from google.cloud import bigquery
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
import os
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()


def is_service_account_key(path: str) -> bool:
    """Check if given JSON file is a service account key."""
    try:
        import json
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('type') == 'service_account' and 'client_email' in data
    except Exception:
        return False


class BigQueryClient:
    """Client for BigQuery operations"""
    
    def __init__(self, project_id: str, credentials_path: str = None):
        """
        Initialize BigQuery client
        
        Args:
            project_id: GCP Project ID
            credentials_path: Path to service account JSON credentials
        """
        self.project_id = project_id
        
        if credentials_path and os.path.exists(credentials_path):
            if is_service_account_key(credentials_path):
                # Use service account credentials
                credentials = service_account.Credentials.from_service_account_file(
                    credentials_path
                )
                self.client = bigquery.Client(
                    project=project_id,
                    credentials=credentials
                )
            else:
                # If the provided file is not a service account key, try OAuth flow
                oauth_path = 'client_secret.json'
                if not os.path.exists(oauth_path):
                    raise FileNotFoundError(
                        "No valid credentials found. Please provide a service account JSON or client_secret.json."
                    )
                # Use OAuth flow to obtain credentials
                flow = InstalledAppFlow.from_client_secrets_file(
                    oauth_path,
                    scopes=[
                        'https://www.googleapis.com/auth/bigquery',
                        'https://www.googleapis.com/auth/cloud-platform',
                    ],
                )
                creds = flow.run_local_server(port=0)
                self.client = bigquery.Client(project=project_id, credentials=creds)
        else:
            # Use default credentials from environment (e.g., gcloud auth application-default login)
            self.client = bigquery.Client(project=project_id)
    
    def list_datasets(self):
        """List all datasets in the project"""
        datasets = list(self.client.list_datasets())
        
        if not datasets:
            return []
        
        dataset_list = []
        for dataset in datasets:
            dataset_list.append(dataset.dataset_id)
        
        return dataset_list
    
    def list_tables(self, dataset_id: str):
        """List all tables in a dataset"""
        dataset_ref = self.client.dataset(dataset_id)
        tables = list(self.client.list_tables(dataset_ref))
        
        if not tables:
            return []
        
        table_list = []
        for table in tables:
            table_list.append(table.table_id)
        
        return table_list
    
    def query(self, sql: str) -> pd.DataFrame:
        """
        Execute a BigQuery query and return results as pandas DataFrame
        
        Args:
            sql: SQL query string
            
        Returns:
            pandas.DataFrame with query results
        """
        query_job = self.client.query(sql)
        results = query_job.to_dataframe()
        return results
    
    def get_table_data(self, table_id: str, limit: int = 10) -> pd.DataFrame:
        """
        Get sample data from a table
        
        Args:
            table_id: Full table ID (dataset.table)
            limit: Number of rows to fetch
            
        Returns:
            pandas.DataFrame with sample data
        """
        sql = f"SELECT * FROM `{self.project_id}.{table_id}` LIMIT {limit}"
        return self.query(sql)


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = BigQueryClient(
        project_id="analisis-finanzas-globales",
        credentials_path="service-account-key.json"  # Or use environment default
    )
    
    # List datasets
    client.list_datasets()
