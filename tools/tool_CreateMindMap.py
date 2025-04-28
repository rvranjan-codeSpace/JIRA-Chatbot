
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
from streamlit_mermaid import st_mermaid


class MindMap():
    def getPrompt(self):
        template = """
            our job is to write the code to generate a colorful mermaid diagram describing the below
            {steps} information only , dont use any other information.You need to only generate the code as output nothing extra.
            Each line in the code must be terminated by ; 
            Code:
            """
        return template
    
    def createMindMap(self,message):
        prompt = self.getPrompt()
        promt_template = ChatPromptTemplate.from_template(prompt)
        chain = promt_template | cons.getModel()
        response=chain.invoke({"steps":message})
        data=response.content
        data=data.replace("`","")
        data=data.replace("mermaid","")
       # st_mermaid(data, key="flow", height="600px")
        print(data)
        return data
      


def create_Mind_Map_node(state: AgentState):
    message = state["messages"]
    last_message = message[-1]
    response= "Mind Map created"
    #data = MindMap().createMindMap(last_message.content)
    return {"messages": [AIMessage(last_message.content)]}
 



