import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from langchain.tools import tool
from jiraAPIKit.create_jira_issue import JiraIssueCreator
import json
from langchain_core.prompts import ChatPromptTemplate
from outputParsers.userStoriesParser import UserStoryParser
import constants.constants as cons
from langgraph.prebuilt import ToolExecutor, ToolInvocation, ToolNode
from jiraAPIKit.createIssueLink import JiraIssueLinkCreator
import json

class JIRATicketCreation(BaseModel):      
    project_id: str = Field(
        description="This is the project ID or the project key to create issue or a Ticket for a particular project"
    )
    issue_Type: str = Field(default="Story",
        description="This is the issue type. It can be User Story, task, Bug", enum=["Story","Bug","Test","Task"]
    )
    issue_Summary: Optional[str] = Field(
        description="Free text to describe the title of the issue"
    )
    issue_Desc: Optional[str] = Field(description="Free text to describe more context to the issue")

    @validator("issue_Type")
    def validate_issue_Type(cls, value) -> str:
        if value.upper() not in ["STORY", "BUG", "TASK", "TEST"]:
            raise ValueError("issue type must be of Story, Bug, Test or Task")
        return value

@tool("JiraTicketCreationTool", args_schema=JIRATicketCreation)
def createIssues(project_id: str, issue_Type: str, issue_Summary: str, issue_Desc: str
) -> str:
    """Use this Tool to create a new the Jira issue"""

    issue_details = {
        "fields":{
        "project": {"key": project_id},
        "description": issue_Desc,
        "summary": issue_Summary,
        "issuetype":{"name":issue_Type}
        }
    }
    output_as_dict=createACriteria_and_Test(issue_Summary,issue_Desc)
    print("issue_details",issue_details)
    print(f"type of AC is:", output_as_dict)
    ac_criteria = None
    if isinstance(output_as_dict.get('testcase_steps'), list):
        ac_criteria = "ACCEPTANCE CRITERIA:\n"+'\n'.join(output_as_dict['AC'])
    else:
        ac_criteria = "ACCEPTANCE CRITERIA:\n"+'\n'+output_as_dict['AC']

    
    issue_Desc=issue_details['fields']['description']+ "\n" + ac_criteria
    issue_details['fields']['description'] = issue_Desc
    story_response = JiraIssueCreator().create_issue(issue_details)
    # Check if error
    if "error" in story_response:
        raise Exception(f"Failed to create Story: {story_response['details']}")
    test_response = createTest_in_JIRA(issue_details,output_as_dict)
    createIssueLink(story_response,test_response, 'Test')
    return story_response

def createIssueLink(story_response, test_response, issue_type):
    # NO NEED TO DO json.loads() anymore
    story_response_json = story_response
    test_response_json = test_response

    link_issue_details = {
        "inwardIssue": {
            "key": story_response_json['key']
        },
        "outwardIssue": {
            "key": test_response_json['key']
        },
        "type": {
            "name": issue_type
        }
    }
    response = JiraIssueLinkCreator().create_issueLink(link_issue_details)
    print(f"issue link created : {response}")

def createACriteria_and_Test(issue_Summary,issue_Desc):
    prompt = getPrompt()
    output_parser= UserStoryParser.create_output_parser()
    format_msg=prompt.format_messages(
        format_instructions=UserStoryParser.get_format_instructions(),
        user_story_title=issue_Summary,
        user_story_description=issue_Desc,
        )
    llm = cons.getModel()
    resp = llm(format_msg)
    output_as_dict = output_parser.parse(resp.content)
    return output_as_dict

def createTest_in_JIRA(issue_details,output_as_dict):
    tools = cons.getTools()
    tool_name = "JiraTestCreationTool"
    tool_executor = ToolExecutor(tools=tools)

    project_id = issue_details['fields']['project']['key']
    issue_Type = "Test"
    print(f"type of test cases steps is:", output_as_dict)
    issue_desc= None
    if isinstance(output_as_dict.get('testcase_steps'), list):
        issue_desc = "TEST STEPS:\n"+'\n'.join(output_as_dict['testcase_steps'])
    else:
        issue_desc = "TEST STEPS:\n"+'\n'+output_as_dict['testcase_steps']
    # Create a dictionary with the required fields
    test_details = {
    "project_id": project_id,
    "issue_Type": issue_Type,
    "issue_Summary": output_as_dict['testcase_summary'],
    "issue_Desc": issue_desc
    }

    # Convert the dictionary to a JSON-formatted string
    tool_input:dict = test_details
    action = ToolInvocation(tool=tool_name, tool_input=tool_input)
    response = tool_executor.invoke(action)
    return response
   

@tool("JiraTestCreationTool", args_schema=JIRATicketCreation)
def createTestCase(project_id: str, issue_Type: str, issue_Summary: str, issue_Desc: str
) -> str:
    """This tool is exclusively to create new test cases in JIRA """

    issue_details = {
        "fields":{
        "project": {"key": project_id},
        "description": issue_Desc,
        "summary": issue_Summary,
        "issuetype":{"name":issue_Type}
        }
    }
    resp= JiraIssueCreator().create_issue(issue_details)
    return resp
   

def getPrompt():
    prompt = ChatPromptTemplate.from_messages([
        ("system",  """
        You are a Quality Engineering Architect with expertise in creating user stories. 
        Based on the provided user story user story title and user story description, you will generate:
        1. **Acceptance Criteria (AC):** List specific criteria required for the story to be considered complete.
        2. **Test Case Summary:** A brief summary of the test case to validate the user story.
        3. **Test Case Steps:** Step-by-step instructions to execute the test case.
        
        The Acceptance Criteria and Test Case Steps should be numbered as:
        1. First item
        2. Second item
        3. Third item
        (Continue numbering sequentially)
        
        Follow the structure:
        {format_instructions}
        """),
    
        ("user",  """
        User Story title: "{user_story_title}"
        User Story Description: "{user_story_description}"
         
        
        Please provide:
        - Acceptance Criteria (AC)
        - Test Case Summary
        - Test Case Steps (Numbered 1, 2, etc.)
        """)
    ])
    return prompt