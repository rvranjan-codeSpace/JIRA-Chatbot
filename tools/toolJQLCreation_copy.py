import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pydantic import BaseModel, Field, validator
from langchain.tools import tool
from typing import List, Optional
import json
import constants.constants as cons
from langgraph.prebuilt import ToolExecutor, ToolInvocation
from langchain_core.prompts import ChatPromptTemplate
from stateGraph.state import AgentState
from langchain.schema import (AIMessage,FunctionMessage)
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from outputParsers.jql_ouputParser import JQLQueryParser
import time


JQL_tool = "JQL_Creation_tool"


class JQL(BaseModel):
    user_input: str = Field(
        description="This is the entireHuman message or user input that will be used along with project_id, userStory_id and testCase_id to create a JQL querry or the mind map"
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

    epic_id: Optional[str] = Field(
        description="This is the Epic ID if the dependent test case needs to be searched only for particular Epic"
    )


@tool(JQL_tool, args_schema=JQL)
def createJQLs(
    user_input: str,
    project_id: str,
    userStory_id: Optional[str] = None,
    testCase_id: Optional[str] = None,
    epic_id: Optional[str]=None
) -> str:
    """Use this Tool 
    -to convert a normal human conversation about JIRA requirement for project, User stories and test cases to conver to JIRA
    - to write Jira Query Langauage(JQL)
    """
      # Define the input variables for the prompt
    if project_id is None:
        userStory_id= "NA"
    if userStory_id is None:
        userStory_id= "NA"
    if testCase_id is None:
        testCase_id = "NA"
    if epic_id is None:
        epic_id = "NA"

    inputs = {
        "user_input": user_input,
        "project_id": project_id,
        "userStory_id": userStory_id,
        "testcase_id": testCase_id,
        "epic_id": epic_id
    }
 
    prompt = getJQLPrompt()
    persisitVectorDb(False)
    time.sleep(1) 
    output_parser= JQLQueryParser.create_output_parser()
    similar_JQL_examples = getSimilarJQL(inputs['user_input'])
    format_msg=prompt.format_messages(
        similar_JQL_examples=similar_JQL_examples,user_query=inputs["user_input"],format_instructions=JQLQueryParser.get_format_instructions(),
        project_id=project_id,
        userStory_id= userStory_id,
        testCase_id= testCase_id,
        epic_id= epic_id
        )
    #chain = prompt | cons.getModel()

    #resp:AIMessage = chain.invoke({"similar_JQL_examples":similar_JQL_examples, "user_query":inputs["user_input"]})
    llm = cons.getModel()
    resp = llm(format_msg)
    output_as_dict = output_parser.parse(resp.content)
    time.sleep(1)
    print("Normal JQL Resp:",output_as_dict["JQL"])
    return output_as_dict["JQL"]

def getJQLPrompt():
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert in creating precise, executable JQL queries for JIRA."),
        ("system", """
            Here are some reference JQL examples for training purposes:
            {similar_JQL_examples}
        """),
        ("system", """
            Common JQL mistakes and corrections:
            Example 1:
            Incorrect JQL: issue in linkedIssues(XSP-27, "is blocked by") AND issuetype = "User Story"
            Reason: 'User Story' is not a valid issuetype.
            Corrected JQL: issue in linkedIssues(XSP-27, "is blocked by") AND issuetype = "Story"
        """),
        ("user", """
            Based on the examples provided, generate an executable JQL query for the following user request: {user_query}.
            
            Replace placeholder values with specifics if available:
            - `project_id`: {project_id}
            - `userStory_id`: {userStory_id}
            - `testCase_id`: {testCase_id}
            - `epic_id`: {epic_id}
            
            Instructions:
            1. Exclude placeholders marked as 'NA' from the final JQL.
            2. Ensure the JQL follows the correct syntax and uses only valid JIRA field values.
            3. The output JQL should be ready for direct execution in JIRA.
            
            {format_instructions}
        """)
    ])
    return prompt
 
def JQLCreator_node(state: AgentState):
    model_name= cons.getModel().get_name()
    tools = [createJQLs]
    message = state["messages"]
    last_message = message[-1]
    tool_executor = ToolExecutor(tools=tools)
    tool_input= None
    if model_name in 'ChatOpenAI':
        tool_input = last_message.additional_kwargslast_message.additional_kwargs["function_call"]["arguments"]
    elif model_name in 'ChatGroq':
        tool_input:dict=json.loads(last_message.additional_kwargs["tool_calls"][-1]["function"]["arguments"])
    else:
         print("Model name is neither Chat OpenAI not Grqo. Check contants.py")

    action = ToolInvocation(tool=JQL_tool, tool_input=tool_input)
    response = tool_executor.invoke(action) 
    ai_message = AIMessage(content=str(response), name=action.tool) # new line added
    resp = {"messages": [ai_message]} # new line added
    #Commentd the below line of code as response was not AI message it was just a string.
    #if isinstance(response,AIMessage):
        #return {"messages": [response]}
    return resp

def getEmbeddingsPath():
    current_dir = os.path.dirname(__file__)
    jql_embedding_path = os.path.join(current_dir, "..", "rag", "jqlembeddings")
    return jql_embedding_path

def persisitVectorDb(persist:bool):
    if persist :
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, "JQL_list.txt")   
        model = cons.getModel()
        text_documents:any
        if os.path.exists(file_path):
            loader=TextLoader(file_path)
            text_documents = loader.load()
            #print(text_documents)
        else:
            print(f"{file_path} not found.")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunked:List[Document]= text_splitter.split_documents(text_documents)
        jql_embedding_path = getEmbeddingsPath()
        if os.path.exists(jql_embedding_path):
            print("persist embeddings")
            db = Chroma.from_documents(chunked,OpenAIEmbeddings(), persist_directory=jql_embedding_path)
            db.persist()
            print("db created")
        else:
            print(f"path doesnot exists:${jql_embedding_path}")
    else:
        print("DB already persisted")   

def getSimilarJQL(userQuery):
    db =  Chroma(persist_directory=getEmbeddingsPath(), embedding_function=OpenAIEmbeddings())
    resp = db.similarity_search(userQuery)
    print(resp[0].page_content)
    return resp[0].page_content

if __name__ == "__main__":
    persisitVectorDb(True)

   
