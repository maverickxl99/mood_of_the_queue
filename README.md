# Mood of the Queue

A real-time mood tracking application for monitoring team sentiment through support tickets. Built with Python, Streamlit, and Google Sheets integration.

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install requirements.txt
   ```

3. Set up Google Sheets:
   - Create a project and enable Google Sheet API on GCP
   - Download the JSON key
   - Create a new Google Sheet named "Mood of the Queue"
   - Share it with your Google Service Account email
   - Create a file `secrets.toml` in the same `directory with main.py` following the format
   ```bash
   [gcp_service_account]
    type = "service_account"
    project_id = "your_project_id"
    private_key_id = 'your_private_key_id'
    private_key = 'your_private_key'
    client_email = 'your_client_email'
    client_id = "your_client_id"
    token_uri = "your_auth_uri"
    auth_provider_x509_cert_url = "your_auth_provider_x509_cert_url"
    client_x509_cert_url = "your_client_x509_cert_url"
   ```
   - Add your service account credentials to `.streamlit/secrets.toml`

4. Run the application:
   ```bash
   streamlit run main.py
   ```

## Instructions

1. Select a mood emoji from the sidebar
2. Add an optional note for context
3. Click "Submit Mood" to log your entry
4. View the mood distribution chart and statistics
5. Check recent entries below the chart
