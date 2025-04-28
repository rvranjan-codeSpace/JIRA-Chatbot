import requests
from requests.auth import HTTPBasicAuth
import json
import os
from constants.config import JIRA_API_TOKEN, JIRA_INSTANCE_URL, JIRA_USERNAME

class JQLExecutor:
    def __init__(self):
        self.url = JIRA_INSTANCE_URL + "/rest/api/3/search"
        self.auth = HTTPBasicAuth(JIRA_USERNAME, JIRA_API_TOKEN)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def execute_JQL(self, JQL) -> str:
        """Execute the JIRA JQL and fetch the dependent issues."""
        print("JQL Query is:", JQL)
        
        payload = json.dumps({
            "expand": ["names", "schema", "operations"],
            "fields": ["*all"],
            "jql": JQL.strip(),
            "startAt": 0
        })

        payload2 = json.dumps({
            "expand": ["names", "schema", "operations"],
            "fields": ["key", "duedate", "assignee", "summary", "status"],
            "jql": JQL.strip(),
            "startAt": 0
        })

        try:
            if "assignee" in JQL or "due" in JQL:
                response = requests.post(self.url, data=payload2, headers=self.headers, auth=self.auth)
                return massageResponse2(response.json())
            else:
                response = requests.post(self.url, data=payload, headers=self.headers, auth=self.auth)
                return massageResponse(response.json())
        except Exception as e:
            return {"normal": f"Exception occurred: {str(e)}", "json": []}


def massageResponse(response_data) -> dict:
    output_string = ""
    json_output = []
    if isinstance(response_data, dict) and 'issues' in response_data:
        for issue in response_data['issues']:
            issue_summary = {
                "Issue ID": issue['key'],
                "Summary": issue['fields']['summary'],
                "Status": issue['fields']['status']['name'],
                "Linked Issues": []
            }

            output_string += f"Issue ID: {issue['key']}\n"
            output_string += f"Summary: {issue['fields']['summary']}\n"
            output_string += f"Status: {issue['fields']['status']['name']}\n"

            issue_links = issue['fields'].get('issuelinks', [])
            if issue_links:
                output_string += "Linked Issues:\n"
                for link in issue_links:
                    if 'outwardIssue' in link:
                        linked_issue = link['outwardIssue']
                        link_type = link['type']['outward']
                        output_string += f" {issue['key']} {link_type.upper()} {linked_issue['key']}\n"
                        output_string += f" Summary: {linked_issue['fields']['summary']}\n"
                        output_string += f" Status: {linked_issue['fields']['status']['name']}\n"

                        issue_summary["Linked Issues"].append({
                            "Linked Issue ID": linked_issue['key'],
                            "Summary": linked_issue['fields']['summary'],
                            "Status": linked_issue['fields']['status']['name'],
                            "Link Type": link_type
                        })

                    if 'inwardIssue' in link:
                        linked_issue = link['inwardIssue']
                        link_type = link['type']['inward']
                        output_string += f" {linked_issue['key']} {link_type.upper()} {issue['key']}\n"
                        output_string += f" Summary: {linked_issue['fields']['summary']}\n"
                        output_string += f" Status: {linked_issue['fields']['status']['name']}\n"

                        issue_summary["Linked Issues"].append({
                            "Linked Issue ID": linked_issue['key'],
                            "Summary": linked_issue['fields']['summary'],
                            "Status": linked_issue['fields']['status']['name'],
                            "Link Type": link_type
                        })
            else:
                output_string += "No linked issues.\n"

            output_string += "-" * 40 + "\n"
            json_output.append(issue_summary)
    else:
        if "errorMessages" in response_data:
            output_string += f"Error: {response_data['errorMessages'][-1]}"
        else:
            output_string += f"Invalid response: {response_data}"

    final_output = {
        "normal": output_string,
        "json": json_output
    }

    print(final_output["normal"])
    return final_output


def massageResponse2(response_data):
    output_string = ""
    json_output = []

    # print("Raw JIRA response:")
    # print(json.dumps(response_data, indent=2))

    if isinstance(response_data, dict) and 'issues' in response_data:
        for issue in response_data['issues']:
            fields = issue.get('fields', {})
            status_name = fields.get('status', {}).get('name', 'No status available')
            due_date = fields.get('duedate', 'No due date available')
            
            issue_summary = {
                "Issue ID": issue['key'],
                "Summary": fields.get('summary', 'No summary'),
                "Status": status_name,
                "Due Date": due_date
            }

            output_string += f"Issue ID: {issue['key']}\n"
            output_string += f"Summary: {issue_summary['Summary']}\n"
            output_string += f"Status: {issue_summary['Status']}\n"
            output_string += f"Due Date: {issue_summary['Due Date']}\n"
            output_string += "-" * 40 + "\n"

            json_output.append(issue_summary)
    else:
        if "errorMessages" in response_data:
            output_string += f"Error: {response_data['errorMessages'][-1]}"
        else:
            output_string += f"Invalid response: {response_data}"

    final_output = {
        "normal": output_string,
        "json": json_output
    }

    print(final_output["normal"])
    return final_output
