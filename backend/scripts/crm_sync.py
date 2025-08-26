"""
HubSpot/Salesforce Lite CRM Sync Script

- Example: Syncs user and lead data to HubSpot and Salesforce via their REST APIs
- Reads new/updated users and leads from local database (stub)
- Posts data to CRM endpoints (stubbed for demo)
"""
import os
import json
 # import requests  # Uncomment if using actual API calls

# Example paths to new/updated user and lead data
USER_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "user.json")
LEAD_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "lead.json")

# Example CRM API endpoints (replace with real endpoints and auth)
HUBSPOT_API_URL = "https://api.hubapi.com/crm/v3/objects/contacts"
SALESFORCE_API_URL = "https://your-instance.salesforce.com/services/data/vXX.X/sobjects/Lead/"
HUBSPOT_API_KEY = os.getenv("HUBSPOT_API_KEY", "demo-key")
SALESFORCE_ACCESS_TOKEN = os.getenv("SALESFORCE_ACCESS_TOKEN", "demo-token")


from typing import Any, Dict

def sync_to_hubspot(user_or_lead: Dict[str, Any]):
    # Stub: Replace with actual POST request
    print(f"Syncing to HubSpot: {user_or_lead}")
    # headers = {"Authorization": f"Bearer {HUBSPOT_API_KEY}", "Content-Type": "application/json"}
    # response = requests.post(HUBSPOT_API_URL, headers=headers, json=user_or_lead)
    # print(response.status_code, response.text)


def sync_to_salesforce(user_or_lead: Dict[str, Any]):
    # Stub: Replace with actual POST request
    print(f"Syncing to Salesforce: {user_or_lead}")
    # headers = {"Authorization": f"Bearer {SALESFORCE_ACCESS_TOKEN}", "Content-Type": "application/json"}
    # response = requests.post(SALESFORCE_API_URL, headers=headers, json=user_or_lead)
    # print(response.status_code, response.text)


def main():
    # Load user and lead data (stubbed)
    for path in [USER_DATA_PATH, LEAD_DATA_PATH]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for entry in data.get("data", []):
                sync_to_hubspot(entry)
                sync_to_salesforce(entry)

    print("CRM sync complete.")

if __name__ == "__main__":
    main()
