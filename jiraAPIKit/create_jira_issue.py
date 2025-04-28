# create_jira_issue.py
import requests
from requests.auth import HTTPBasicAuth
import json
import os
from constants.config import JIRA_INSTANCE_URL, JIRA_USERNAME, JIRA_API_TOKEN
from requests.auth import HTTPBasicAuth

class JiraIssueCreator:
    def __init__(self):
        # Initialize JIRA instance URL and authentication
        self.url = JIRA_INSTANCE_URL + "/rest/api/2/issue"
        self.auth = HTTPBasicAuth(JIRA_USERNAME, JIRA_API_TOKEN)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def create_issue(self, body) -> dict:
        """Create a JIRA issue with the given body."""
        payload = json.dumps(body)
        response = requests.post(self.url, data=payload, headers=self.headers, auth=self.auth)

        try:
            response.raise_for_status()  # Raises error if HTTP response is bad (4xx or 5xx)
            return response.json()       # Return parsed JSON directly
        except requests.exceptions.RequestException as e:
            print(f"❌ Error while creating issue: {e}")
            print(f"❌ Response text: {response.text}")
            return {"error": str(e), "details": response.text}

