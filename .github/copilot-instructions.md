# Colombia Economic Insights - Project Setup

This project extracts economic data from Google Cloud BigQuery.

## Project Details
- **Type**: Python Data Analysis
- **GCP Project**: analisis-finanzas-globales
- **Purpose**: Extract data from BigQuery, process, and integrate with Looker

## Setup Steps Completed
- ✓ Created project structure
- ✓ Created requirements.txt with BigQuery dependencies
- ✓ Created BigQuery client module
- ✓ Created main script for data extraction
- ✓ Created configuration files and examples

## Next Actions

1. **Install dependencies**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure GCP Credentials**:
   - Download service account key from: https://console.cloud.google.com/
   - Place as `service-account-key.json` in project root
   - OR set `GOOGLE_APPLICATION_CREDENTIALS` environment variable

3. **Test the connection**:
   ```bash
   python src/main.py
   ```

4. **Run automated analysis**:
   ```bash
   python src/analysis.py
   ```

5. **Review generated reports** in `output/` folder

## Completed Features
- ✅ BigQuery connection and data extraction
- ✅ Automated statistical analysis and reporting
- ✅ CSV export of tables and statistics
- ✅ Year-over-year trend analysis
- ✅ Outlier detection
- ⏳ Looker integration (next step)
- ⏳ Automated visualizations (matplotlib compatibility issue)

## Project Structure
- `src/bigquery_client.py` - BigQuery client class
- `src/main.py` - Main extraction script
- `src/analysis.py` - Statistical analysis and automated reporting
- `requirements.txt` - Python dependencies
- `.env.example` - Environment variables template
- `output/` - Generated reports and tables (auto-created)
