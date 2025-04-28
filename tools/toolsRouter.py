from pydantic import BaseModel, Field, validator
from typing import List, Optional
from langchain.tools import tool
from typing import Literal
import json
from constants.constants import getModel
from langchain_core.prompts import ChatPromptTemplate
from stateGraph.state import AgentState
from langchain_core.utils.function_calling import convert_to_openai_function
from langgraph.prebuilt import ToolExecutor, ToolInvocation, ToolNode



class Router(BaseModel):
   
    mesages: Literal["create_issue","update_issue","create_testcase","get_issue", "create_rtm","general_chat","get_dependent_user_stories"] = Field(...,
        description= """""
        Given the user input the router routes it to create_issue_tool,create_test_xray,get_issue,create_rtm (requiremnt Tracebility matrix),wiki_search
        """)

tools = []
@tool("dispatcherTool")
def dispatcherTool(user_input
) -> str:
    """Use this Tool route the user query realted to JIRA Applicaition"""
    system= """you are an expert in routing user_input who is inteeacting with JIRA chatbot.
    Use you thought and make a right choice from list of tools which is :["create_issue","create_testcase","get_issue", "create_rtm","general_chat"]
    Given the user input is regarding create issues or User story in JIRA , route it to create_issue
    Given the user input is regarding update issues or User story in JIRA , route it to update_issue
    Given the user input is regarding create Test case/test case  JIRA-Xraytool , route it to create_testcase
    Given the user input is regarding create Requirement Traceiblity Matrix(RTM) , route it to create_rtm
    Given the user input is regarding get dependent user stories or test case  , route it to get_dependent_user_stories
    Given the user input is regarding none of the above,route it to general_chat
    """
    route_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human","{user_input}")
        ])
    structured_llm_router = getModel().with_structured_output(Router)
    chain = route_prompt | structured_llm_router
    response = chain.invoke({"user_input":user_input})
    print(response)
    return response
   





