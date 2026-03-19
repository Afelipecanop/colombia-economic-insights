"""
Looker Studio Integration for Colombia Economic Insights
Automatically upload data to Google Looker Studio
"""

import os
import pandas as pd
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle

# Looker Studio API scopes
SCOPES = [
    'https://www.googleapis.com/auth/datastudio',
    'https://www.googleapis.com/auth/drive.file'
]

# Google Drive API scopes for file upload
DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive.file']


def is_service_account_key(path: str) -> bool:
    """Return True if the JSON file at `path` looks like a service account key."""
    try:
        import json
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('type') == 'service_account' and 'client_email' in data
    except Exception:
        return False


class LookerStudioUploader:
    """Upload data to Google Looker Studio automatically"""

    def __init__(self, credentials_path: str = None):
        """Initialize Looker Studio uploader

        Args:
            credentials_path: Path to credentials JSON file
        """
        self.credentials_path = credentials_path or 'service-account-key.json'
        self.creds = None
        self.datastudio_service = None
        self.drive_service = None

    def authenticate(self):
        """Authenticate with Google APIs"""
        try:
            # Try to load existing credentials
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    self.creds = pickle.load(token)

            # If credentials are invalid or don't exist, get new ones
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    # Prefer service account if the file exists and is valid
                    if os.path.exists(self.credentials_path) and is_service_account_key(self.credentials_path):
                        from google.oauth2 import service_account
                        self.creds = service_account.Credentials.from_service_account_file(
                            self.credentials_path,
                            scopes=SCOPES + DRIVE_SCOPES
                        )
                    else:
                        # Fallback to OAuth flow using client_secret.json
                        if not os.path.exists('client_secret.json'):
                            raise FileNotFoundError(
                                "No valid service account key found and 'client_secret.json' is missing."
                            )
                        print("⚠️  Service account key not found/invalid; using OAuth flow instead.")
                        flow = InstalledAppFlow.from_client_secrets_file(
                            'client_secret.json', SCOPES + DRIVE_SCOPES
                        )
                        self.creds = flow.run_local_server(port=0)

                # Save credentials for future use
                with open('token.pickle', 'wb') as token:
                    pickle.dump(self.creds, token)

            # Build services
            self.datastudio_service = build('datastudio', 'v1', credentials=self.creds)
            self.drive_service = build('drive', 'v3', credentials=self.creds)

            return True

        except Exception as e:
            return False

    def upload_csv_to_drive(self, csv_file_path: str, filename: str = None) -> str:
        """
        Upload CSV file to Google Drive

        Args:
            csv_file_path: Path to local CSV file
            filename: Name for the file in Drive (optional)

        Returns:
            File ID of uploaded file
        """
        if not self.drive_service:
            raise ValueError("Not authenticated. Call authenticate() first.")

        if not filename:
            filename = os.path.basename(csv_file_path)

        file_metadata = {
            'name': filename,
            'mimeType': 'text/csv'
        }

        media = MediaFileUpload(
            csv_file_path,
            mimetype='text/csv',
            resumable=True
        )

        file = self.drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        file_id = file.get('id')

        # Make file publicly readable (required for Looker Studio)
        self.drive_service.permissions().create(
            fileId=file_id,
            body={
                'type': 'anyone',
                'role': 'reader'
            }
        ).execute()

        return file_id

    def create_or_update_dataset(self, file_id: str, dataset_name: str, csv_columns: list) -> str:
        """
        Create or update a Looker Studio dataset

        Args:
            file_id: Google Drive file ID
            dataset_name: Name for the dataset
            csv_columns: List of column configurations

        Returns:
            Dataset ID
        """
        if not self.datastudio_service:
            raise ValueError("Not authenticated. Call authenticate() first.")

        # Create data source configuration
        data_source_config = {
            'name': dataset_name,
            'dataSourceType': 'BIGQUERY',  # We'll use BigQuery as intermediary
            'calculatedFields': [],
            'parameters': []
        }

        try:
            # Create data source
            data_source = self.datastudio_service.datasources().create(
                body=data_source_config
            ).execute()

            data_source_id = data_source['dataSourceId']

            return data_source_id

        except Exception as e:
            return None

    def generate_report_link(self, dataset_id: str = None) -> str:
        """
        Generate a link to create a new Looker Studio report

        Args:
            dataset_id: Optional dataset ID to include

        Returns:
            URL to create new report
        """
        base_url = "https://lookerstudio.google.com/reporting/create"

        if dataset_id:
            return f"{base_url}?c.reportId={dataset_id}"
        else:
            return base_url

    def upload_analysis_results(self, output_dir: str = 'output') -> dict:
        """
        Upload all analysis CSV files to Looker Studio

        Args:
            output_dir: Directory containing CSV files

        Returns:
            Dictionary with upload results
        """
        if not self.authenticate():
            return {"error": "Authentication failed"}

        results = {
            'uploaded_files': [],
            'datasets': [],
            'report_link': self.generate_report_link()
        }

        # Find all CSV files in output directory
        csv_files = [f for f in os.listdir(output_dir) if f.endswith('.csv')]

        if not csv_files:
            print("⚠️ No CSV files found in output directory")
            return results

        for csv_file in csv_files:
            csv_path = os.path.join(output_dir, csv_file)

            try:
                # Upload to Drive
                file_id = self.upload_csv_to_drive(csv_path, csv_file)

                # Try to create dataset (this might not work with current API limitations)
                dataset_name = csv_file.replace('.csv', '').replace('_', ' ').title()
                dataset_id = self.create_or_update_dataset(file_id, dataset_name, [])

                results['uploaded_files'].append({
                    'filename': csv_file,
                    'drive_file_id': file_id,
                    'dataset_id': dataset_id
                })

            except Exception as e:
                results['uploaded_files'].append({
                    'filename': csv_file,
                    'error': str(e)
                })

        return results


# Example usage
if __name__ == "__main__":
    # Initialize uploader
    uploader = LookerStudioUploader()

    # Upload all analysis results
    results = uploader.upload_analysis_results('output')

    print("\n📊 Upload Results:")
    for file_info in results.get('uploaded_files', []):
        if 'drive_file_id' in file_info:
            print(f"✓ {file_info['filename']} -> Drive ID: {file_info['drive_file_id']}")
        else:
            print(f"✗ {file_info['filename']} -> Error: {file_info.get('error', 'Unknown')}")