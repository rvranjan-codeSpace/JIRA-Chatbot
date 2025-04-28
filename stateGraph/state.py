import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from typing_extensions import TypedDict
from typing import Annotated, Sequence
from langchain_core.messages.base import BaseMessage
from typing import Literal, Any
from langgraph.graph.message import add_messages
import operator

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    chat_history:Sequence[BaseMessage]

