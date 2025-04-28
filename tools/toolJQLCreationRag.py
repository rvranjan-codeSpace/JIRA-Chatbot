import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from langchain.tools import tool
from jiraAPIKit.create_jira_issue import JiraIssueCreator
import json
import constants.constants as cons
from langchain.schema import (AIMessage,FunctionMessage)
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings,OpenAIEmbeddings
# from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores import Chroma
# from langchain_chroma.vectorstores import Chroma
from langchain_core.documents import Document
from constants.config import GPT_CONFIG



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
            # db = Chroma.from_documents(chunked,OpenAIEmbeddings(), persist_directory=jql_embedding_path)
            db = Chroma(
    persist_directory=getEmbeddingsPath(),
    embedding_function=OpenAIEmbeddings(openai_api_key=GPT_CONFIG["gpt_api_key"])
)
            # db.persist()
            print("db created")
        else:
            print(f"path doesnot exists:${jql_embedding_path}")
    else:
        print("DB already persisted")   

def getVectorDb():
    # db =  Chroma(persist_directory=getEmbeddingsPath(), embedding_function=OpenAIEmbeddings())
    db = Chroma(
    persist_directory=getEmbeddingsPath(),
    embedding_function=OpenAIEmbeddings(openai_api_key=GPT_CONFIG["gpt_api_key"])
)
    resp = db.similarity_search("create a mind map for all test cases blocked by User story ABC")
    print(resp[0].page_content)

if __name__ == "__main__":
    persisitVectorDb(persist=False)
    getVectorDb()
  



