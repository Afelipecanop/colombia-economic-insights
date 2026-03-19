"""
Economic Data Analysis for Colombia
Generates statistical reports, tables, and visualizations from BigQuery data
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from bigquery_client import BigQueryClient
from looker_integration import LookerStudioUploader

# Create output directories
os.makedirs('output', exist_ok=True)
os.makedirs('output/charts', exist_ok=True)


class EconomicAnalyzer:
    """Analyzer for economic data with statistical reports"""

    def __init__(self, bigquery_client: BigQueryClient):
        """Initialize with BigQuery client"""
        self.client = bigquery_client
        self.data = None

    def load_data(self, table_id: str, limit: int = None):
        """Load data from BigQuery table"""
        # table_id should be in format: project.dataset.table
        if limit:
            sql = f"SELECT * FROM `{table_id}` LIMIT {limit}"
        else:
            sql = f"SELECT * FROM `{table_id}`"

        self.data = self.client.query(sql)
        return self.data

    def generate_statistics_report(self, value_column: str = 'value', year_column: str = 'year'):
        """Generate comprehensive statistical report"""
        if self.data is None:
            raise ValueError("No data loaded. Call load_data() first.")

        stats = {}

        # Basic statistics
        stats['basic'] = {
            'count': len(self.data),
            'mean': self.data[value_column].mean(),
            'median': self.data[value_column].median(),
            'std': self.data[value_column].std(),
            'min': self.data[value_column].min(),
            'max': self.data[value_column].max(),
            'range': self.data[value_column].max() - self.data[value_column].min()
        }

        # Statistics by year (if year column exists)
        if year_column in self.data.columns:
            yearly_stats = self.data.groupby(year_column)[value_column].agg([
                'count', 'mean', 'median', 'std', 'min', 'max'
            ]).round(4)

            # Year-over-year change
            yearly_stats.loc[:, 'yoy_change'] = yearly_stats['mean'].pct_change() * 100
            stats['yearly'] = yearly_stats

        # Percentiles
        percentiles = [0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99]
        stats['percentiles'] = self.data[value_column].quantile(percentiles).round(4)

        # Outlier analysis
        Q1 = self.data[value_column].quantile(0.25)
        Q3 = self.data[value_column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR

        outliers = self.data[
            (self.data[value_column] < lower_bound) |
            (self.data[value_column] > upper_bound)
        ]

        stats['outliers'] = {
            'count': len(outliers),
            'lower_bound': round(lower_bound, 4),
            'upper_bound': round(upper_bound, 4),
            'outlier_values': outliers[value_column].tolist() if len(outliers) <= 10 else f"{len(outliers)} outliers found"
        }

        return stats

    def create_summary_table(self, value_column: str = 'value', year_column: str = 'year'):
        """Create summary table with key metrics"""
        if self.data is None:
            raise ValueError("No data loaded. Call load_data() first.")

        summary = pd.DataFrame({
            'Metric': [
                'Total Records',
                'Average Value',
                'Median Value',
                'Standard Deviation',
                'Minimum Value',
                'Maximum Value',
                'Value Range',
                'Years Covered'
            ],
            'Value': [
                len(self.data),
                f"{self.data[value_column].mean():.4f}",
                f"{self.data[value_column].median():.4f}",
                f"{self.data[value_column].std():.4f}",
                f"{self.data[value_column].min():.4f}",
                f"{self.data[value_column].max():.4f}",
                f"{self.data[value_column].max() - self.data[value_column].min():.4f}",
                f"{self.data[year_column].min()} - {self.data[year_column].max()}" if year_column in self.data.columns else 'N/A'
            ]
        })

        return summary

    def export_report(self, stats: dict, summary_table: pd.DataFrame, filename_prefix: str = "economic_report"):
        """Export statistical report to CSV files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Export basic statistics
        basic_stats_df = pd.DataFrame.from_dict(stats['basic'], orient='index', columns=['Value'])
        basic_stats_df.to_csv(f'output/{filename_prefix}_basic_stats_{timestamp}.csv')

        # Export yearly statistics
        if 'yearly' in stats:
            stats['yearly'].to_csv(f'output/{filename_prefix}_yearly_stats_{timestamp}.csv')

        # Export percentiles
        percentiles_df = pd.DataFrame(stats['percentiles'], columns=['Value'])
        percentiles_df.index.name = 'Percentile'
        percentiles_df.to_csv(f'output/{filename_prefix}_percentiles_{timestamp}.csv')

        # Export summary table
        summary_table.to_csv(f'output/{filename_prefix}_summary_{timestamp}.csv', index=False)

        # Export outliers info
        outliers_info = pd.DataFrame.from_dict(stats['outliers'], orient='index', columns=['Info'])
        outliers_info.to_csv(f'output/{filename_prefix}_outliers_{timestamp}.csv')

        return {
            'basic_stats': f'output/{filename_prefix}_basic_stats_{timestamp}.csv',
            'yearly_stats': f'output/{filename_prefix}_yearly_stats_{timestamp}.csv' if 'yearly' in stats else None,
            'percentiles': f'output/{filename_prefix}_percentiles_{timestamp}.csv',
            'summary': f'output/{filename_prefix}_summary_{timestamp}.csv',
            'outliers': f'output/{filename_prefix}_outliers_{timestamp}.csv'
        }

    def create_visualizations(self, value_column: str = 'value', year_column: str = 'year', filename_prefix: str = "economic"):
        """Create and save automated visualizations"""
        if self.data is None:
            raise ValueError("No data loaded. Call load_data() first.")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        charts_created = []

        try:
            # Simple time series
            if year_column in self.data.columns:
                fig = plt.figure(figsize=(8, 5))
                plt.plot(self.data[year_column], self.data[value_column], 'b-')
                plt.title('Inflacion Colombia')
                plt.xlabel('Year')
                plt.ylabel('Value (%)')
                plt.savefig(f'output/charts/{filename_prefix}_timeseries_{timestamp}.png')
                charts_created.append(f'output/charts/{filename_prefix}_timeseries_{timestamp}.png')

            # Simple histogram
            fig = plt.figure(figsize=(6, 4))
            plt.hist(self.data[value_column], bins=8, alpha=0.7)
            plt.title('Distribution')
            plt.xlabel('Value (%)')
            plt.ylabel('Count')
            plt.savefig(f'output/charts/{filename_prefix}_histogram_{timestamp}.png')
            charts_created.append(f'output/charts/{filename_prefix}_histogram_{timestamp}.png')

        except Exception as e:
            pass  # Analysis continues without charts

        # Generate statistics
        stats = self.generate_statistics_report(value_column, year_column)

        # Create summary table
        summary = self.create_summary_table(value_column, year_column)

        # Export reports
        files = self.export_report(stats, summary, "colombia_economic")

        # Create visualizations
        charts = self.create_visualizations(value_column, year_column, "colombia_economic")

        return charts_created

    def run_complete_analysis(self, table_id: str, value_column: str = 'value', year_column: str = 'year', upload_to_looker: bool = False):
        """Run complete analysis pipeline with reports and optional Looker Studio upload"""

        # Load data
        self.load_data(table_id)

        # Generate statistics
        stats = self.generate_statistics_report(value_column, year_column)

        # Create summary table
        summary = self.create_summary_table(value_column, year_column)

        # Export reports
        files = self.export_report(stats, summary, "colombia_economic")

        # Create visualizations
        print("\n📊 Generating visualizations...")
        charts = self.create_visualizations(value_column, year_column, "colombia_economic")

        # Optional: Upload to Looker Studio
        looker_results = None
        if upload_to_looker:
            print("\n📤 Uploading results to Looker Studio...")
            uploader = LookerStudioUploader()
            looker_results = uploader.upload_analysis_results('output')

        return stats, summary, files, charts, looker_results


# Example usage
if __name__ == "__main__":
    # Initialize analyzer
    analyzer = EconomicAnalyzer(
        project_id="analisis-finanzas-globales",
        credentials_path="service-account-key.json"  # Or use environment default
    )

    # Run complete analysis
    stats, summary, files, charts = analyzer.run_complete_analysis(
        table_id="analysis_inflation.colombia_inflation",
        value_column="value",
        year_column="year"
    )

    # Display summary
    print("\n📋 Summary Table:")
    print(summary.to_string(index=False))

    print(f"\n📈 Generated {len(charts)} charts:")
    for chart in charts:
        print(f"  - {chart}")