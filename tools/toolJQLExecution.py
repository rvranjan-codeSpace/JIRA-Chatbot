from pydantic import BaseModel, Field, validator
from typing import List, Optional
from langchain.tools import tool
from jiraAPIKit.executeJQL import JQLExecutor
import json
import constants.constants as cons
from langgraph.prebuilt import ToolExecutor, ToolInvocation
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from stateGraph.state import AgentState
from langchain.schema import (AIMessage,FunctionMessage)


JQL_tool = "JQL_Execution_tool"
class JQLExecution(BaseModel):
    jql: str = Field(
        description="JQL query that needs to be executed"
    )

@tool("JQL_Execution_tool", args_schema=JQLExecution)
def executeJQL(jql: str) -> any:
    """Use this Tool to execute a JQL"""
      # Define the input variables for the prompt
    resp =  JQLExecutor().execute_JQL(jql)
    return resp

def JQLExecutor_node(state: AgentState):
    message = state["messages"]
    last_message = message[-1]
    tool_executor = ToolExecutor(tools=[executeJQL])
    tool_input: str = (last_message.content).strip()
    # tool_input["chat_history"]=chat_history
    action = ToolInvocation(tool=JQL_tool, tool_input=tool_input)
    response = tool_executor.invoke(action)
    formatted_response =AIMessage(response['normal'])
    return {"messages": [formatted_response]}

