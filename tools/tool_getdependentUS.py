from pydantic import BaseModel, Field, validator
from typing import List, Optional
from langchain.tools import tool
from jiraAPIKit.create_jira_issue import  JiraIssueCreator
import json
from stateGraph import state
from stateGraph.state import AgentState

class DependentIssues(BaseModel):  
    user_input:str = Field(
        description="This is the Human message or user input that will be used along with project_id, userStory_id and testCase_id to create a JQL querry"
    )

    project_id: str = Field(
        description="This is the project ID for which dependendent user stories or dependent test cases in the entire Project needs to be searched"
    )

    userStory_id: Optional[str] = Field(
        description="This is the User story ID if the dependency needs to be searched only for individual User story"
    )

    testCase_id: Optional[str] = Field(
        description="This is the Test case ID if the dependent test case needs to be searched only for individual Test cases"
    )

@tool("US_Dependency_CreationTool", args_schema=DependentIssues)
def create_DependentUS_MindMap(user_input:str,project_id:str,userStory_id:str,testCase_id:str)-> str:
    """Use this Tool to create a MIND MAP
    Use this Tool to create a  DEPENDENCY TABLE or Dependency Graph 
    Use this Tool to create a Flow chart
    Use this tool to create a JIRA Query Language (JQL)
    """

def AgentChat_node(state:AgentState):
    # model_with_tools = getModelWithTools(model)
    # state["chat_history"]= chat_history
    # user_input = state["messages"]
    # last_message = user_input[-1]
    # response = model_with_tools.invoke(user_input)
    #return {"messages": [response]}\
    pass