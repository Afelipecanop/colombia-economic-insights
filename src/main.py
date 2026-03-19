"""
Main script for Colombia Economic Insights
Extract economic data from BigQuery and run complete analysis
"""

import os
import sys
import argparse
from dotenv import load_dotenv
from bigquery_client import BigQueryClient
from analysis import EconomicAnalyzer

# Load environment variables
load_dotenv()


def main():
    """Main execution function"""

    parser = argparse.ArgumentParser(description='Colombia Economic Insights - BigQuery Data Analysis')
    parser.add_argument('--table', type=str, help='BigQuery table ID to analyze')
    parser.add_argument('--looker', action='store_true', help='Upload results to Looker Studio')
    parser.add_argument('--test-connection', action='store_true', help='Test BigQuery connection only')

    args = parser.parse_args()

    # Initialize BigQuery client
    project_id = "analisis-finanzas-globales"

    # Try to use credentials file if it exists
    credentials_path = None
    if os.path.exists("service-account-key.json"):
        credentials_path = "service-account-key.json"

    try:
        client = BigQueryClient(
            project_id=project_id,
            credentials_path=credentials_path
        )

        # Test connection mode
        if args.test_connection:
            datasets = client.list_datasets()
            if datasets:
                pass  # Connection successful
            else:
                pass  # No datasets found
            return

        # Run complete analysis
        if args.table:
            # Initialize analyzer
            analyzer = EconomicAnalyzer(client)

            # Run complete analysis with optional Looker upload
            stats, summary, files, charts, looker_results = analyzer.run_complete_analysis(
                table_id=args.table,
                upload_to_looker=args.looker
            )

        else:
            # Show available tables
            datasets = client.list_datasets()

            if datasets:
                for dataset in datasets:
                    tables = client.list_tables(dataset)
            else:
                pass

        print("\n✓ Operation completed successfully!")

    except Exception as e:
        print(f"✗ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("  1. Ensure GCP credentials are configured")
        print("  2. Check table ID format: project.dataset.table")
        print("  3. Verify BigQuery permissions")
        sys.exit(1)


if __name__ == "__main__":
    main()
