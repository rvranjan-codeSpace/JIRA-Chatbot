import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from stateGraph.state import AgentState
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import BaseMessage
from langchain.tools import tool
from pydantic import BaseModel, Field, validator
from typing import Annotated, Sequence
import constants.constants as cons

class ChatToold(BaseModel):      
    chat_history: list = Field(
        description="chat_history is the history of messages by HumanMessage and AIMessage")
    user_input:str=Field(description="This is the last message asked by the user to the Human to chatbot")

def getAgentPrompt():
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful JIRA Assistant. you need to create JIRA story in project with the available",
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ]
    )
    return prompt
@tool("chatTool")
def toolChat(user_input:str,chat_history:list) -> str:
    """Use this Tool just to chat with the llm model.
    This tool is NOT resposible for CREATING a JIRA story/Issue
    This tool is NOT resposible for UPDATING a JIRA story/Issue
    This tool is NOT resposible for CREATING a Requirement Tracebility Matrix (RTM)
    """
    chain= getAgentPrompt()| cons.getModel()
    response = chain.invoke({"chat_history":chat_history,"input":user_input})
    print(response)
    return response

class Chat:
     
    def getChatPrompt(self):
        prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a a simple chat prompt that will help the user for coomunicate with JIRA applicaiton
                JIRA is a popular web-based project management tool developed by Atlassian. It is widely used by software development
                You also have the chat history with the user below:
                """
                  
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
        ])
        return prompt

    
    def getllm_with_chatTool(self):
        tools=[toolChat]
        model=cons.getModel()
        llm_chat= model.bind_tools(tools)
        llm_chain = self.getChatPrompt()|llm_chat
        return llm_chain

if __name__== "__main__":
     chain = Chat().getllm_with_chatTool()
     chat_history=[]
     agent_scratchpad=[]
     resp = chain.invoke({"input":"hi","chat_history":chat_history})
     print(resp)
      
    
  
    

