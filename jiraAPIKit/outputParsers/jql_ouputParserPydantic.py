import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from langchain.output_parsers import StructuredOutputParser,PydanticOutputParser
from typing import List
from pydantic import BaseModel, Field

class JQLQueryParser(BaseModel):
    jql: str = Field(description="This is the executable JQL that can execute in JIRA")
    reasoning: str = Field(description="This is the reason the JQL has been created")

    @staticmethod
    def create_output_parser()->PydanticOutputParser:
       jql_parser=PydanticOutputParser(pydantic_object=JQLQueryParser)
       return jql_parser

    @staticmethod
    def get_formatInstructions() -> str:
        # Return format instructions from the output parser
        output_parser = JQLQueryParser.create_output_parser()
        format_instructions = output_parser.get_format_instructions()
        return format_instructions

if __name__ == "__main__":
    print(JQLQueryParser.get_formatInstructions())


