import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from langgraph.graph import Graph, StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from typing import TypedDict
from stateGraph.state import AgentState
from llmmodel.modelFactory import Model
from constants.constants import getModel,getTools
from tools.toolsRouter import dispatcherTool
from langchain.schema import SystemMessage, HumanMessage, AIMessage, FunctionMessage, BaseMessage
from tools.toolJIRA import createIssues
from tools.toolCreate_RTM import createRTM
from tools.toolJQLCreation import JQLCreator_node
from tools.toolJQLExecution import JQLExecutor_node
from tools.tool_CreateMindMap import create_Mind_Map_node
from langgraph.prebuilt import ToolExecutor, ToolInvocation, ToolNode
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain.tools import tool
from langchain_core.language_models import BaseChatModel
from typing import Annotated, Sequence
import time
import json

chat_history:Sequence[BaseMessage]=[]
#tools = [toolChat,createIssues, createRTM]
def processChat(user_input, chat_history:list,*, compiledGraph:CompiledStateGraph)->str:
    resp:str
    for output in compiledGraph.stream(user_input):
        output
        for key, value in output.items():
            #print(f"Output from {key}:")
            #print("-----")
            #print(value)
            resp=value
            print("\n-----\n")
            value
            key
        output
    resp
    resp = resp["messages"][-1].content
    chat_history.append(AIMessage(resp))
    #print("message:",resp)
    return resp

def getModelWithTools(model:BaseChatModel)->BaseChatModel:
    tools = getTools()
    openai_functions = [convert_to_openai_function(t) for t in tools]
    llm_with_tools = model.bind_tools(openai_functions)
    return llm_with_tools
      
def AgentChat_node(state:AgentState):
    model = getModel()
    model_with_tools = getModelWithTools(model)
    state["chat_history"]= chat_history
    user_input = state["messages"]
    response = model_with_tools.invoke(user_input)
    time.sleep(2)
    return {"messages": [response]}


def JIRA_Ticket_Creation_node(state:AgentState):
    tools = getTools()
    message = state["messages"]
    last_message = message[-1]
    #tool_name = last_message.additional_kwargs["function_call"]["name"] 
    tool_name = last_message.additional_kwargs["tool_calls"][-1]["function"]["name"]
    tool_executor = ToolExecutor(tools=tools)
    tool_input:dict=json.loads(last_message.additional_kwargs["tool_calls"][-1]["function"]["arguments"])
    #tool_input:dict = json.loads(last_message.additional_kwargs["function_call"]["arguments"])
    #tool_input["chat_history"]=chat_history
    action = ToolInvocation(tool=tool_name, tool_input=tool_input)
    response = tool_executor.invoke(action)
    function_message = FunctionMessage(content=str(response), name=action.tool)
    return {"messages": [function_message]}

# def getWorkflow_path_node(state:AgentState):
#     model_name = getModel().get_name()
#     message = state["messages"]
#     last_message = message[-1]
#     if model_name in 'ChatOpenAI':
#         if last_message.additional_kwargs:
#         #if "US_Dependency_CreationTool" in last_message.additional_kwargs["function_call"]["name"]:
#              if "US_Dependency_CreationTool" in last_message.additional_kwargs["function_call"]["name"]:
#                 return "JQLCreator_node"
#              elif "JiraTicketCreationTool" in last_message.additional_kwargs["function_call"]["name"]:
#                 return "continue"
#         else:
#             return "end"
#     elif model_name in 'ChatGroq':
#         if last_message.additional_kwargs:
#         #if "US_Dependency_CreationTool" in last_message.additional_kwargs["function_call"]["name"]:
#             if "US_Dependency_CreationTool" in last_message.additional_kwargs["tool_calls"][-1]["function"]["name"]:
#                 return "JQLCreator_node"
#             elif "JiraTicketCreationTool" in last_message.additional_kwargs["tool_calls"][-1]["function"]["name"]:
#                 return "continue"
#         else:
#             return "end"
#     else:
#         print("Model name is neither Chat OpenAI not Grqo. Check contants.py")

def getWorkflow_path_node(state:AgentState):
    model_name = getModel().get_name()
    message = state["messages"]
    last_message = message[-1]
    print("last_message",last_message)
    if model_name in 'ChatOpenAI':
        if last_message.additional_kwargs and "function_call" in last_message.additional_kwargs:
            fn_name = last_message.additional_kwargs["function_call"]["name"]
            if "US_Dependency_CreationTool" in fn_name:
                return "JQLCreator_node"
            elif "JiraTicketCreationTool" in fn_name:
                return "continue"
        else:
            return "end"
    elif model_name in 'ChatGroq':
        if last_message.additional_kwargs and "tool_calls" in last_message.additional_kwargs:
            fn_name = last_message.additional_kwargs["tool_calls"][-1]["function"]["name"]
            if "US_Dependency_CreationTool" in fn_name:
                return "JQLCreator_node"
            elif "JiraTicketCreationTool" in fn_name:
                return "continue"
        else:
            return "end"
    else:
        print("Model name is neither Chat OpenAI nor Groq. Check constants.py")

def getJIRAWorkflowGraph()->CompiledStateGraph:
    workflow = StateGraph(state_schema=AgentState)
    workflow.add_node("START_CHAT", AgentChat_node)
    workflow.add_node("TOOL_TICKET_CREATOR", JIRA_Ticket_Creation_node)
    workflow.add_node("TOOL_JQL_CREATOR",JQLCreator_node)
    workflow.add_node("TOOL_JQL_EXECUTOR",JQLExecutor_node)
    workflow.add_node("TOOL_MIND_MAP_NODE",create_Mind_Map_node)
   # workflow.add_node("CREATE_ISSUE", CreateIsuue_node)
    workflow.add_conditional_edges("START_CHAT",getWorkflow_path_node,path_map={
        "JQLCreator_node":"TOOL_JQL_CREATOR",
        "continue":"TOOL_TICKET_CREATOR",
        "end":END
    })
    workflow.add_edge("TOOL_JQL_CREATOR", "TOOL_JQL_EXECUTOR")
    workflow.add_edge("TOOL_JQL_EXECUTOR", "TOOL_MIND_MAP_NODE")
    workflow.add_edge("TOOL_JQL_EXECUTOR", END)
    workflow.add_edge("TOOL_TICKET_CREATOR", "START_CHAT")
    workflow.set_entry_point("START_CHAT")
    app:CompiledStateGraph = workflow.compile()
    app.get_graph().draw_mermaid_png()
    graph_image_bytes = app.get_graph().draw_mermaid_png()

    # Save the PNG bytes to a file
    with open("workflow_graph.png", "wb") as file:
        file.write(graph_image_bytes)

    return app  


def callGraph():
    app:CompiledStateGraph =getJIRAWorkflowGraph()
    while True:
        user_input = input("you: ")
        chat_history.append(HumanMessage(user_input))
        formatted_user_input = {"messages": [HumanMessage(content=user_input)]}
        if (user_input.lower()) == "exit":
            break
        response = processChat(
            user_input=formatted_user_input, chat_history=chat_history, compiledGraph=app
        )
        #print("JIRA ASSITANT:"+response)
      
if __name__ == "__main__":
    callGraph()

def getWorkflow_path_node_backup(state:AgentState):
    message = state["messages"]
    last_message = message[-1]
    if "US_Dependency_CreationTool" in last_message.additional_kwargs:
        return "JQLCreator_node"
    if "function_call" in last_message.additional_kwargs:
        return "continue"
    else:
        return "end"
    
def getWorkflow_path_node_issue(state:AgentState):
    message = state["messages"]
    last_message = message[-1]
    if "function_call" in last_message.additional_kwargs:
        return "continue"
    else:
        return "end"

   
