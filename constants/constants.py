import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llmmodel.modelFactory import Model
from langchain_core.language_models import BaseChatModel
from tools.toolChat import toolChat
from tools.toolJIRA import createIssues, createTestCase
from tools.toolJQLCreation import createJQLs
from langchain.schema import BaseMessage
from tools.tool_getdependentUS import create_DependentUS_MindMap
from typing import Sequence


GEMMA_9B= "Gemma2-9b-It"
GEMMA_7B="gemma-7b-it"
GPT_4_TURBO="gpt-4-turbo"

GROQ_MODEL_TYPE= GEMMA_9B
OPENAI_MODEL=GPT_4_TURBO


def getModel(modelName="GROQ"):
    model = None
    if modelName in 'GROQ':
        model = Model("Groq", GROQ_MODEL_TYPE).getModel()
    elif modelName in "OPENAI":
       model = Model("openai", OPENAI_MODEL).getModel()
    else:
        model = Model("Groq", GROQ_MODEL_TYPE).getModel()
    return model        

def getTools():
    tools = [toolChat,createIssues,createJQLs,create_DependentUS_MindMap,createTestCase]
    return tools

def getChatHistory():
    chat_history:Sequence[BaseMessage]=[]
