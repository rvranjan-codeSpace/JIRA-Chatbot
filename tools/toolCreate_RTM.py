from pydantic import BaseModel, Field, validator
from typing import List, Optional
from langchain.tools import tool
from jiraAPIKit.create_jira_issue import  JiraIssueCreator
import json

class RTMCreation(BaseModel):      
    project_id: str = Field(
        description="This is the project ID or the project KEY to create issue for a particular project"
    )

@tool("RTMCreationTool", args_schema=RTMCreation)
def createRTM(   project_id:str)-> str:
    """Use this Tool to create a Requirement Traciblity Matrix also called RTM from a JIRA Project"""

    issue_details = {
        "fields":{
        "project": {"key": project_id},
        }
    }
    temp_issue_detials = json.dumps(issue_details)
    #print(temp_issue_detials)
    resp= JiraIssueCreator().create_issue(issue_details)
    return resp